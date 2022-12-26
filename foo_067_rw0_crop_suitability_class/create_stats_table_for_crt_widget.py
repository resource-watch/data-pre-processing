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
import sys
from dotenv import load_dotenv
load_dotenv()

utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import logging

######
# NOTE: this script requires that you run the other two scripts in this repo beforehand -- it relies on the tifs in your
# data_dir. To run, follow these steps:
    # 1. Run rice_ensemble_processing.py script
    # 2. Run foo_067_rw0_crop_suitability_class_processing.py
    # 3. Run create_stats_table_for_crt_widget.py
######

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.info('Executing script for creating stats table based on crop suitability class rasters')

def reclass_and_calculate_zonal_stats(raster_list, admin):
    """Reclassifies the supplied tif file from a continuous to a categorical raster

        Parameters:
            raster_list: list of rasters to reclass and calculate stats on
            admin: admin boundary from GeoPandas DF to use as zonal stats summarizing unit. GeoPandas DF must have
                these columns: 'the_geom', 'name_0'
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
        classes = [-9, -1, 0, 1, 1000.01, 2500.01, 4000.01, 5500.01, 7000.01, 8500.01]
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

        ## calculate zonal stats ##
        # define the categories for the zonal stats to calculate
        cmap = {1: 'Ocean',
                2: 'No Cultivation',
                3: 'Not Suitable',
                4: 'Very Marginal',
                5: 'Marginal',
                6: 'Moderate',
                7: 'Medium',
                8: 'Good',
                9: 'High',
                10: 'Very High'}

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
        # union all the dataframes together
        final_df = pd.concat(df_list, axis=0)

    return final_df


def get_country_geom(country_name):
    """Utility to request the country geometry from CARTO table

        Parameters:
            country_name (string): country name to get geometry for processing
    """
    # send data request
    url = "https://wri-rw.carto.com/api/v2/sql?q=SELECT cartodb_id, gid_0, name_0, the_geom, the_geom_webmercator FROM gadm36_0 WHERE name_0 = '" + country_name + "'"
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    # prep country vector data for processing, use json_normalize to extract data into Pandas DF
    admin_boundaries = pd.json_normalize(data, "rows")
    # convert geom column from WKB to a geoseries using geopandas
    geom = gpd.GeoSeries.from_wkb(admin_boundaries['the_geom'], crs=4326)
    # append converted geom column to pandas dataframe
    admin_boundaries['the_geom'] = geom
    # convert pandas df to geopandas df
    boundaries_gpd = gpd.GeoDataFrame(admin_boundaries, geometry='the_geom', crs=4326)

    return boundaries_gpd


# Define data dir for loading tif files
# define dataset name
dataset_name = 'foo_067_rw0_crop_suitability_class'
data_dir = util_files.prep_dirs(dataset_name)

'''
Process coffee rasters
'''

logger.info('Processing coffee rasters')
# create a list of coffee rasters to process
coffee_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cof*_edit.tif'):
        coffee_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
coffee_df_list = []

# coffee country list (based off of countries with SPAM 2010 production values > 0)
#testing_country_list = ['Argentina', 'Colombia', 'India']
coffee_country_list = ['Belize', 'Bolivia', 'Brazil', 'Burundi', 'Cameroon', 'China', 'Colombia', 'Costa Rica', 'Cuba',
                       'Democratic Republic of the Congo', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Ethiopia',
                       'Guadeloupe', 'Guatemala', 'Haiti', 'Honduras', 'India', 'Indonesia', 'Jamaica', 'Kenya', 'Malawi', 'Malaysia',
                       'Martinique', 'Mexico', 'Mozambique', 'Myanmar',  'Nepal', 'Nicaragua', 'Panama', 'Papua New Guinea', 'Paraguay',
                       'Peru', 'Puerto Rico', 'Rwanda', 'Sao Tome and Principe', 'Saint Vincent and the Grenadines', 'Suriname',
                       'Tanzania', 'Timor-Leste', 'Tonga', 'Uganda', 'United States', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in coffee_country_list:
    # get country geom from Carto Table
    try:
        bgpd = get_country_geom(country)
    except:
        print('!! No geometry for:', country)
    # calculate zonal stats
    stats = reclass_and_calculate_zonal_stats(coffee_rasters, bgpd)
    coffee_df_list.append(stats)

# concatenate the final DFs (union, e.g. stack on top of one another)
coffee_stats_df = pd.concat(coffee_df_list, axis=0)
# rename column 'variable' to 'crop_suitability_class'
coffee_stats_df.rename({'variable': 'crop_suitability_class'}, axis=1, inplace=True)

'''
Process cotton rasters
'''

logger.info('Processing cotton rasters')
# create a list of cotton rasters to process
cotton_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*cot*_edit.tif'):
        cotton_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
cotton_df_list = []

# cotton country list (based off of countries with SPAM 2010 production values > 0)
cotton_country_list = ['Afghanistan', 'Albania', 'Algeria', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Australia', 'Azerbaijan',
                       'Bangladesh', 'Benin', 'Bolivia', 'Botswana', 'Brazil', 'Bulgaria', 'Burkina Faso', 'Burundi',  'Cote dIvoire',
                       'Cambodia', 'Cameroon', 'Central African Republic', 'Chad', 'China', 'Colombia', 'Costa Rica', 'Democratic Republic of the Congo',
                       'Ecuador', 'Egypt', 'El Salvador', 'Ethiopia', 'Gambia', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea',
                       'Guinea-Bissau', 'Haiti', 'Honduras', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Kazakhstan', 'Kenya',
                       'Kyrgyzstan', 'Laos', 'Macedonia', 'Madagascar', 'Malawi', 'Mali', 'Mexico', 'Montserrat', 'Morocco', 'Mozambique',
                       'Myanmar', 'Nepal', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'Pakistan', 'Paraguay', 'Peru', 'Philippines',
                       'Romania', 'Saint Kitts and Nevis', 'Senegal', 'Somalia', 'South Africa', 'South Korea', 'Spain', 'Sudan',
                       'Swaziland', 'Syria', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tunisia', 'Turkey', 'Turkmenistan',
                       'Uganda', 'United States', 'Uzbekistan', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in cotton_country_list:
    # get country geom from Carto Table
    try:
        bgpd = get_country_geom(country)
    except:
        print('!! No geometry for:', country)
    # calculate zonal stats
    stats = reclass_and_calculate_zonal_stats(cotton_rasters, bgpd)
    cotton_df_list.append(stats)

# concatenate the final DFs (union, e.g. stack on top of one another)
cotton_stats_df = pd.concat(cotton_df_list, axis=0)
# rename column 'variable' to 'crop_suitability_class'
cotton_stats_df.rename({'variable': 'crop_suitability_class'}, axis=1, inplace=True)


'''
Process rice rasters
'''

logger.info('Processing rice rasters')
# create a list of rice rasters to process
rice_rasters = []
for filename in os.listdir(data_dir):
    if fnmatch.fnmatch(filename, '*rcw_edit.tif') or fnmatch.fnmatch(filename, '*rcd_edit.tif'):
        rice_rasters.append(os.path.join(data_dir, filename))

# create an empty list to collect final dfs
rice_df_list = []

# rice country list (based off of countries with SPAM 2010 production values > 0)
rice_country_list = ['Afghanistan', 'Algeria', 'Angola', 'Argentina', 'Australia', 'Azerbaijan', 'Bangladesh', 'Belize', 'Benin',
                     'Bhutan', 'Bolivia', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cote dIvoire', 'Cambodia',
                     'Cameroon', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Cuba',
                     'Democratic Republic of the Congo', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Ethiopia',
                     'Fiji', 'France', 'French Guiana', 'Gabon', 'Gambia', 'Ghana', 'Greece', 'Guatemala', 'Guinea', 'Guinea-Bissau',
                     'Guyana', 'Haiti', 'Honduras', 'Hungary', 'India', 'Indonesia', 'Iran', 'Iraq', 'Italy', 'Jamaica', 'Japan',
                     'Kazakhstan', 'Kenya', 'Kyrgyzstan', 'Laos', 'Liberia', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Mali',
                     'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Morocco', 'Mozambique', 'Myanmar', 'Nepal', 'Nicaragua',
                     'Niger', 'Nigeria', 'North Korea', 'Pakistan', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines',
                     'Portugal', 'Republic of Congo', 'Romania', 'Russia', 'Rwanda', 'Senegal', 'Sierra Leone', 'Solomon Islands',
                     'Somalia', 'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Tajikistan',
                     'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Trinidad and Tobago', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine',
                     'United States', 'Uruguay', 'Uzbekistan', 'Venezuela', 'Vietnam', 'Zambia', 'Zimbabwe']

# calculate zonal statistics of crop suitability rasters by country and add to a dataframe, and create a dataframe list
for country in rice_country_list:
    # get country geom from Carto Table
    try:
        bgpd = get_country_geom(country)
    except:
        print('!! No geometry for:', country)
    # calculate zonal stats
    stats = reclass_and_calculate_zonal_stats(rice_rasters, bgpd)
    rice_df_list.append(stats)

# concatenate the final DFs (union, e.g. stack on top of one another)
rice_stats_df = pd.concat(rice_df_list, axis=0)
# rename column 'variable' to 'crop_suitability_class'
rice_stats_df.rename({'variable': 'crop_suitability_class'}, axis=1, inplace=True)

'''
Save dataframes as CSVs for upload to Carto
'''

logger.info('Creating CSVs')
# create list of final dataframes
final_stats_df_list = [coffee_stats_df, cotton_stats_df, rice_stats_df]
# concatenate DFs together
crop_suitability_class_stats_df = pd.concat(final_stats_df_list, axis=0).reset_index()

# save final stats DF to CSV
crop_suitability_class_stats = os.path.join(data_dir, 'crt_crop_suitability_class_zonal_stats.csv')
crop_suitability_class_stats_df.to_csv(crop_suitability_class_stats, index=False)

# 1 CSV should now be saved to data_dir and uploaded to Carto DB


'''
Upload processed data to Carto
'''
from cartoframes.auth import set_default_credentials
from cartoframes import read_carto, to_carto, update_privacy_table, delete_table

logger.info('Uploading processed data to Carto.')

# authenticate carto account
CARTO_USER = os.getenv('CARTO_WRI_RW_USER')
CARTO_KEY = os.getenv('CARTO_WRI_RW_KEY')
set_default_credentials(username=CARTO_USER, base_url="https://{user}.carto.com/".format(user=CARTO_USER),api_key=CARTO_KEY)


# upload data frame to Carto
to_carto(crop_suitability_class_stats_df, dataset_name + '_edit', if_exists='replace')

# set privacy to 'link' so table is accessible but not published
update_privacy_table(dataset_name + '_edit', 'link')


