
import pandas as pd
import geopandas as gpd
import numpy as np
import urllib
import glob
import io
import requests
import json
import os
import sys
import tabula
import dotenv
dotenv.load_dotenv('C:\\Users\\Jason.Winik\\OneDrive - World Resources Institute\\Documents\\GitHub\\cred\\.env')
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
gdal_path = os.getenv('GDAL_DIR')
if gdal_path not in sys.path:
    sys.path.append(gdal_path)
import util_files
import util_cloud
import util_carto
import logging
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
# this should be a table name that is not currently in use
dataset_name = 'cli_017_rw1_glacier_locations' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''

# download the data from the source
url = "https://www.glims.org/download/latest"
raw_data_file = os.path.join(data_dir,os.path.basename(url)+'.zip')
r = urllib.request.urlretrieve(url, raw_data_file)
# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process Data
'''
#need polygon and point

# load in the polygon shapefile
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, 'glims_points.shp', 'glims_polygon.shp'))
gdf = gpd.read_file(shapefile)

# convert the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integer
gdf['PROTECT'] = gdf['PROTECT'].astype(int)
gdf['PROTECT_FE'] = gdf['PROTECT_FE'].astype(int)
gdf['METADATA_I'] = gdf['METADATA_I'].astype(int)

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')
# create an index column to use as cartodb_id
gdf['cartodb_id'] = gdf.index

# reorder the columns
gdf = gdf[['cartodb_id'] + list(gdf)[:-1]]

# save processed dataset to shapefile
gdf.to_file(processed_data_file,driver='ESRI Shapefile')

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK')

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
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
#Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))