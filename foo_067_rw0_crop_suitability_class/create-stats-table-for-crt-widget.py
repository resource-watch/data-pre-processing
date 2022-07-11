import pandas as pd
import geopandas as gpd
#import rasterio as rio
import requests
import json
#from shapely.geometry import mapping
import xarray as xr
#import rioxarray as rxr
import rasterio
import numpy as np
#import rasterstats
import os
from rasterstats import zonal_stats
import fnmatch


# Define function to reclassify the raster
def reclassify_raster(raster):
    '''Re-classifies a continuous raster into a categorical one'''

    # create bins to reclassify the data
    classes = [-9, -1, 0, 1001, 2501, 4001, 5551, 7001, 8501]

    # apply the classes to the raster
    raster_classes = xr.apply_ufunc(np.digitize, array, classes)

    return raster_classes


# Define function to calculate zonal statistics
def calculate_zonal_stats(raster, admin, raster_classes):
    '''Calculaute the zonal statistics between a raster and the geometry of an admin boundary'''

    # get info on the raster name to append to zonal results
    raster_name = os.path.splitext(os.path.basename(raster))[0]

    # find scenario info, e.g. historic, rcp45, rcp85
    if fnmatch.fnmatch(raster_name, '*rcp4*'):
        scenario = 'rcp4p5'
    elif fnmatch.fnmatch(raster_name, '*rcp8*'):
        scenario = 'rcp8p5'
    else:
        scenario = 'historic'

    # find year ranges
    if fnmatch.fnmatch(raster_name, '*2020s*'):
        year = '2020s'
    elif fnmatch.fnmatch(raster_name, '*2050s*'):
        year = '2050s'
    else:
        year = '2000s'

    # find technology info = irrigated (gravity or irrigated) OR rainfed
    if fnmatch.fnmatch(raster_name, '*suHg*') or fnmatch.fnmatch(raster_name, '*suHi'):
        tech = 'irrigated'
    else:
        tech = 'rainfed'

    # find crop info, e.g. rcw (wetland rice), rcd (dryland rice), cot (cotton), cof (coffee)
    if fnmatch.fnmatch(raster_name, '*rcw*'):
        crop = 'wetland rice'
    elif fnmatch.fnmatch(raster_name, '*rcd*'):
        crop = 'dryland rice'
    elif fnmatch.fnmatch(raster_name, '*cof*'):
        crop = 'coffee'
    else:
        crop = 'cotton'

        # define the categories for the zonal stats to calculate
        # Very High = vh
        # High = h
        # Good = g
        # Medium = med
        # Moderate = mod
        # Marginal = mar
        # Very Marginal = vm
        # Not Suitable = ns
        # Not cultivated = nc

    cmap = {1: 'ocean',
            2: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'nc',
            3: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'ns',
            4: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'vm',
            5: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'mar',
            6: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'mod',
            7: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'g',
            8: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'h',
            9: year + '_' + scenario + '_' + tech + '_' + crop + '_' + 'vh'}

    zonal_results = zonal_stats(bgpd['the_geom'],
                                raster_classes,
                                cmap=cmap,
                                affine=trans,
                                categorical=True,
                                category_map=cmap,
                                nodata=1)
    # stats='count')

    return zonal_results, admin['name_0'][0]


# Load vector data (country boundaries)
# only loading Argentina for now
response = requests.get("https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE geostore_prod='7ef0a48e34649db114730c06146b9382'")
boundaries = json.loads(response.content.decode('utf-8'))

# prep country vector data for processing
# use json_normalize to extract data in correct format
country = pd.json_normalize(boundaries, "rows")

# convert geom columns from WKB to a geoseries using geopandas
geom = gpd.GeoSeries.from_wkb(country['the_geom'], crs=4326)

# append converted columns to pandas dataframe, country
country['the_geom'] = geom

# convert country pandas df to geopandas df
bgpd = gpd.GeoDataFrame(country, geometry='the_geom', crs=4326)


# Load raster data (crop suitability class tifs)
data_dir = '/Users/alexsweeney/Documents/github-repos/data-pre-processing/foo_067_rw0_crop_suitability_class/data'

coffee_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cof*_edit.tif'):
        coffee_rasters.append(filename)
        print(filename)

all_stats = []
for raster in coffee_rasters:
    with rasterio.open(raster) as src:
        array = src.read(1)
        trans = src.transform
        profile = src.profile
    print(raster)
    rc = reclassify_raster(raster)
    zs = calculate_zonal_stats(raster, bgpd, rc)
    all_stats.append(zs)

print(all_stats)

## TODO figure out how to pipe results into a pandas dataframe iteratively