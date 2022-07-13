import pandas as pd
import geopandas as gpd
import requests
import json
import xarray as xr
import rasterio
import numpy as np
import os
from rasterstats import zonal_stats
import fnmatch


def reclass_and_calculate_zonal_stats(raster_list, admin):
    """
    TODO

    Args: raster_list: list of rasters to reclass and calculate stats on
          admin: geopandas dataframe of admin boundaries
              -- must have these columns: 'the_geom', 'name_0', and 'gid_0'
    """

    # reclassify coffee rasters and calculate zonal statistics
    all_stats = []
    for raster in raster_list:
        ## open raster ##
        with rasterio.open(raster) as src:
            array = src.read(1)
            trans = src.transform
            profile = src.profile

        ## reclassify raster ##
        # define bins to reclassify raster data
        classes = [-9, -1, 0, 1001, 2501, 4001, 5551, 7001, 8501]
        # apply the classes to the raster
        raster_classes = xr.apply_ufunc(np.digitize, array, classes)

        ## get raster naming info to put into zonal stats output ##
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

        ## export raster to tif file for QA/QC ##
        # Define the profile to write to a geotiff file
        # write the reclassified data to a geotiff file, copying the profile information from the original tif
        #profile_out = profile.copy()
        #profile_out.update(nodata=1)

        # write to Geotiff
        #with rasterio.open(os.path.join(data_dir, scenario + year + tech + crop + '_rc.tif'), 'w',
        #                   **profile_out) as dst:
        #    dst.write(raster_classes, 1)

        ## calculate zonal stats ##
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
                2: 'not cultivated',
                3: 'not suitable',
                4: 'very marginal',
                5: 'marginal',
                6: 'moderate',
                7: 'good',
                8: 'high',
                9: 'very high'}

        zonal_results = zonal_stats(admin['the_geom'],
                                    raster_classes,
                                    cmap=cmap,
                                    affine=trans,
                                    categorical=True,
                                    category_map=cmap,
                                    nodata=1)
        # add raster info to zonal stats dictionary
        zonal_results[0]['raster'] = year + '_' + scenario + '_' + tech + '_' + crop
        # add country info to zonal stats dictionary
        zonal_results[0]['country'] = admin['name_0'][0]
        # add zonal_results to all_stats list
        all_stats.append(zonal_results)

    ## add zonal stats to pandas dataframe ##
    # create an empty dataframe list
    df_list = []

    index = 0
    for index in range(len(all_stats)):
        # set up naming of the dataframe for each loop
        i = str(index + 1)
        df_name = 'df' + i
        # create a pandas dataframe to collect the zonal stats for each raster iteration
        df_name = pd.DataFrame(all_stats[index])
        # use melt to convert from long-form to wide-form
        df_name = pd.melt(df_name, id_vars=['raster', 'country'])
        # add the dataframe to the dataframe list
        df_list.append(df_name)
        # union all of the dataframes together
        final_df = pd.concat(df_list, axis=0)

    return final_df


# Define data dir
# Load raster data (crop suitability class tifs)
data_dir = '/Users/alexsweeney/Documents/github-repos/data-pre-processing/foo_067_rw0_crop_suitability_class/data/'

'''
Process coffee rasters
'''

# create a list of coffee rasters to process
coffee_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cof*_edit.tif'):
        coffee_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
coffee_df_list = []

# list of countries to get stats on  # TODO add country list in
country_list = ['Argentina', 'Colombia', 'India']

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in country_list:
    print(country)
    url = "https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE name_0 = '" + country + "'"
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    # prep country vector data for processing, use json_normalize to extract data in correct format
    admin_boundaries = pd.json_normalize(data, "rows")
    # convert geom columns from WKB to a geoseries using geopandas
    geom = gpd.GeoSeries.from_wkb(admin_boundaries['the_geom'], crs=4326)
    # append converted columns to pandas dataframe, country
    admin_boundaries['the_geom'] = geom
    # convert country pandas df to geopandas df
    bgpd = gpd.GeoDataFrame(admin_boundaries, geometry='the_geom', crs=4326)
    # calculate stats
    stats = reclass_and_calculate_zonal_stats(coffee_rasters, bgpd)
    coffee_df_list.append(stats)

print(coffee_df_list)

# concatenate the final DFs (union, e.g. stack on top of one another)
coffee_stats_df = pd.concat(coffee_df_list, axis=0)
# TODO rename column variable to 'suitability_class'
coffee_stats_df
