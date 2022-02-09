import logging
import geopandas as gpd
import pandas as pd
import numpy as np
import glob
import os
import sys
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
# Create list to store both the csv file and zipped shapefile paths
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
Process shdi shapefile data
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
processed_shp_file = os.path.join(data_dir, 'soc_086_subnational_hdi_shapefile_edit'+'.shp')
# save processed dataset to shapefile
gdf_shapefile.to_file(processed_shp_file,driver='ESRI Shapefile')

'''
Process shdi data from csv file
'''

# read in data to pandas dataframe
df = pd.read_csv(raw_data_file[0])
# convert the column names to lowercase
df.columns = [x.lower() for x in df.columns]
# convert tables from wide form (each year is a column) to long form
df = pd.melt(df,id_vars=['country', 'iso_code','level','gdlcode','region'],var_name='year', value_name='shdi_value')
# change type of columns
df['year'] = df['year'].astype('int64')
# create a new column 'datetime' to store years as datetime objects
df['datetime'] = [datetime(x, 1, 1) for x in df.year]
# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name +'_edit.csv')
df.to_csv(processed_data_file, index=False)

'''
Upload original data and processed data to Amazon S3 storage
'''

# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))
        
# Copy the processed shdi shapefile into a zipped file to upload to S3
processed_shp_dir = os.path.join(data_dir, 'soc_086_subnational_hdi_shapefile_edit'+'.zip')
# Find al the necessary components of the shapefile 
processed_shp_files = glob.glob(os.path.join(data_dir, 'soc_086_subnational_hdi_shapefile_edit'+'.*'))
with ZipFile(processed_shp_dir,'w') as zip:
    for file in processed_shp_files:
           zip.write(file, os.path.basename(file))
# Upload processed shapefile to S3
uploaded = util_cloud.aws_upload(processed_shp_dir, aws_bucket, s3_prefix+os.path.basename(processed_shp_dir))

# Copy processed csv into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))

'''
Upload processed data to Carto
'''
# Upload processed shdi shapefile to carto
util_carto.upload_to_carto(processed_shp_dir, 'LINK')
# Upload processed shdi data to carto
util_carto.upload_to_carto(processed_data_file, 'LINK')