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
def reclassify_raster(array):
    """
    # TODO create better docstrings
    Re-classifies a continuous raster into a categorical one
    """

    # create bins to reclassify the data
    classes = [-9, -1, 0, 1001, 2501, 4001, 5551, 7001, 8501]

    # apply the classes to the raster
    raster_classes = xr.apply_ufunc(np.digitize, array, classes)

    return raster_classes


# Define function to calculate zonal statistics
def calculate_zonal_stats(raster, admin, raster_classes):
    """
    # TODO create better docstrings
    Calculaute the zonal statistics between a raster and the geometry of an admin boundary
    """

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
    if fnmatch.fnmatch(raster_name, '*suHg*') or fnmatch.fnmatch(raster_name, '*suHi*'):
        tech = 'irrigated'
    else:
        tech = 'rainfed'

    # find crop info, e.g. rcw (wetland rice), rcd (dryland rice), cot (cotton), cof (coffee)
    if fnmatch.fnmatch(raster_name, '*rcw*'):
        crop = 'wetland_rice'
    elif fnmatch.fnmatch(raster_name, '*rcd*'):
        crop = 'dryland_rice'
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

    return zonal_results


# create function to define all processing steps
def process_stats(raster_list):
    """
    # TODO create better docstrings
    all the processing steps -- reclassifies rasters, claculates zonal statistics, puts them into a
    pandas dataframe, and returns it
    """

    # reclassify coffee rasters and calculate zonal statistics
    all_stats = []
    for r in raster_list:
        with rasterio.open(r) as src:
            array = src.read(1)
            trans = src.transform
            profile = src.profile
        print(r)  # TODO remove
        rc = reclassify_raster(array)
        zs = calculate_zonal_stats(r, bgpd, rc)
        all_stats.append(zs)

    # add zonal stats to pandas dataframe and prep for upload to Carto Table
    # create empty list of dataframes to append to
    df_list = []

    index = 0
    for index in range(len(all_stats)):
        # set up naming of the dataframe for each loop
        i = str(index + 1)
        df_name = 'df' + i
        # create a pandase dataframe to collect the zonal stats for each raster
        df_name = pd.DataFrame(all_stats[index])
        # add the dataframe to the dataframe list
        df_list.append(df_name)
        # union all of the dataframes together (will append on right side)
        final_df = pd.concat(df_list, axis=1)
        # add the country name to the dataframe
        final_df.insert(loc=0, column='country', value=bgpd['name_0'])
        # add ISO code to the dataframe
        final_df.insert(loc=0, column='ISO3', value=bgpd['gid_0'])

    return final_df


# Load raster data (crop suitability class tifs)
data_dir = '/Users/alexsweeney/Documents/github-repos/data-pre-processing/foo_067_rw0_crop_suitability_class/data/'

# define list of countries to compute stats on
country_list = ['Argentina', 'Colombia', 'India']  # TODO add full country list

'''
Process Coffee rasters
'''
# create a list of coffee rasters to process
coffee_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cof*_edit.tif'):
        coffee_rasters.append(os.path.join(data_dir, filename))
        # print(coffee_rasters) # TODO remove

# create an empty list to collect final dfs
coffee_df_list = []

# calculate zonal statistics of crop suitability rasters by country, add to a dataframe, and append to a dataframe list
for country in country_list:
    print(country)  #TODO remove
    url = "https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE name_0 = '" + country + "'"
    response = requests.get(url)
    boundaries = json.loads(response.content.decode('utf-8'))
    # prep country vector data for processing, use json_normalize to extract data in correct format
    admin = pd.json_normalize(boundaries, "rows")
    # convert geom columns from WKB to a geoseries using geopandas
    geom = gpd.GeoSeries.from_wkb(admin['the_geom'], crs=4326)
    # append converted columns to pandas dataframe, country
    admin['the_geom'] = geom
    # convert country pandas df to geopandas df
    bgpd = gpd.GeoDataFrame(admin, geometry='the_geom', crs=4326)
    # calculate stats
    stats = process_stats(coffee_rasters)
    coffee_df_list.append(stats)

print(coffee_df_list)  # TODO remove

# concatenate the final DFs (union, e.g. stack on top of one another)
coffee_stats_df = pd.concat(coffee_df_list, axis=0)
coffee_stats_df  # TODO remove

'''
Process rice rasters
'''
# create a list of rice rasters to process
rice_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*rcw_edit.tif') or fnmatch.fnmatch(filename, '*rcd_edit.tif'):
        rice_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
rice_df_list = []

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in country_list:
    print(country)  # TODO remove
    url = "https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE name_0 = '" + country + "'"
    response = requests.get(url)
    boundaries = json.loads(response.content.decode('utf-8'))
    # prep country vector data for processing, use json_normalize to extract data in correct format
    admin = pd.json_normalize(boundaries, "rows")
    # convert geom columns from WKB to a geoseries using geopandas
    geom = gpd.GeoSeries.from_wkb(admin['the_geom'], crs=4326)
    # append converted columns to pandas dataframe, country
    admin['the_geom'] = geom
    # convert country pandas df to geopandas df
    bgpd = gpd.GeoDataFrame(admin, geometry='the_geom', crs=4326)
    # calculate stats
    stats = process_stats(rice_rasters)
    rice_df_list.append(stats)

print(rice_df_list)  # TODO remove

# concatenate the final DFs (union, e.g. stack on top of one another)
rice_stats_df = pd.concat(rice_df_list, axis=0)
rice_stats_df  # TODO remove

'''
Process cotton rasters
'''

# create a list of cotton rasters to process
cotton_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cot*_edit.tif') or fnmatch.fnmatch(filename, '*cot*_edit.tif'):
        cotton_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
cotton_df_list = []

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in country_list:
    print(country)  # TODO remove
    url = "https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE name_0 = '" + country + "'"
    response = requests.get(url)
    boundaries = json.loads(response.content.decode('utf-8'))
    # prep country vector data for processing, use json_normalize to extract data in correct format
    admin = pd.json_normalize(boundaries, "rows")
    # convert geom columns from WKB to a geoseries using geopandas
    geom = gpd.GeoSeries.from_wkb(admin['the_geom'], crs=4326)
    # append converted columns to pandas dataframe, country
    admin['the_geom'] = geom
    # convert country pandas df to geopandas df
    bgpd = gpd.GeoDataFrame(admin, geometry='the_geom', crs=4326)
    # calculate stats
    stats = process_stats(cotton_rasters)
    cotton_df_list.append(stats)

print(cotton_df_list)  # TODO remove

# concatenate the final DFs (union, e.g. stack on top of one another)
cotton_stats_df = pd.concat(cotton_df_list, axis=0)
cotton_stats_df  # TODO remove
