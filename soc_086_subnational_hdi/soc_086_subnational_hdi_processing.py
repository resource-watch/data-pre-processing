import logging
import geopandas as gpd
import pandas as pd
import numpy as np
from collections import OrderedDict
from shapely.geometry import Polygon, Point, mapping
import glob
import os
import sys
import dotenv
import requests
from datetime import datetime
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import shutil
from zipfile import ZipFile

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of table on Carto where you want to upload data
# using preexisting table for this dataset
dataset_name = 'soc_086_subnational_hdi' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded from:
https://globaldatalab.org/shdi/view/shdi/

Shapefile for subnational boundaries:
https://globaldatalab.org/shdi/shapefiles/
'''

# download the data from the source
logger.info('Downloading raw data')
downloads = []
downloads.append(glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'GDL-Sub-national-HDI-data.csv'))[0])
downloads.append(glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'GDL Shapefiles V4.zip'))[0])

# move this file into your data directory
# Create file paths where the excel files will be stored
raw_data_file = [os.path.join(data_dir,os.path.basename(download)) for download in downloads]
for index, download in enumerate(downloads):
    shutil.move(download,raw_data_file[index])

# unzip source data
raw_data_file_unzipped = raw_data_file[1].split('.')[0]
zip_ref = ZipFile(raw_data_file[1], 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''

# load in the polygon shapefile of sub-national human development index boundaries
shapefile= glob.glob(os.path.join(raw_data_file_unzipped, '*.shp' ))[0]
gdf_shapefile = gpd.read_file(shapefile)

# reproject geometries to epsg 4326
gdf_shapefile['geometry'] = gdf_shapefile['geometry'].to_crs(epsg=4326)

# convert the column names to lowercase
gdf_shapefile.columns = [x.lower() for x in gdf_shapefile.columns]
# replace all NaN with None
gdf_shapefile=gdf_shapefile.where((pd.notnull(gdf_shapefile)), None)
# create an index column to use as cartodb_id
gdf_shapefile['cartodb_id'] = gdf_shapefile.index
# reorder the columns
gdf_shapefile = gdf_shapefile[['cartodb_id'] + list(gdf_shapefile)[:-1]]

# create a path to save the processed shapefile later
processed_shp_file = os.path.join(data_dir, 'soc_086_test'+'.shp')
# save processed dataset to shapefile
gdf_shapefile.to_file(processed_shp_file,driver='ESRI Shapefile')

'''
Upload processed data to Carto
'''
# Copy the processed data into a zipped file to upload to S3
processed_shp_dir = os.path.join(data_dir, 'soc_086_test'+'_edit.zip')
# Find al the necessary components of the shapefile 
processed_shp_files = glob.glob(os.path.join(data_dir, 'soc_086_test'+'.*'))
with ZipFile(processed_shp_dir,'w') as zip:
     for file in processed_shp_files:
        zip.write(file, os.path.basename(file))
# upload the shapefile to Carto
util_carto.upload_to_carto(processed_shp_dir, 'LINK', collision_strategy = 'overwrite')

