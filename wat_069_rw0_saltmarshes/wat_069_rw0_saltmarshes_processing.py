import logging
import geopandas as gpd
import glob
import os
import sys
import dotenv
import requests
import dotenv
utils_path = os.path.join(os.getenv('PROCESSING_DIR'),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import shutil
from zipfile import ZipFile
import urllib

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
dataset_name = 'wat_069_rw0_saltmarshes'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://wcmc.io/WCMC_027'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'WCMC027_Saltmarsh_v6_1.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''

# load in the polygon shapefile
path = os.path.join(raw_data_file_unzipped, raw_data_file_unzipped[5:], '01_Data', '*Py_v6_1.shp')
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, raw_data_file_unzipped[5:], '01_Data', '*Py_v6_1.shp'))[0]
gdf = gpd.read_file(shapefile)

# convert the data type of column 'METADATA_I' to integer
gdf['METADATA_I'] = gdf['METADATA_I'].astype(int)

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')

# Reproject geometries to epsg 4326
gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)

logger.info('Saving processed shapefile.')
# save processed dataset to shapefile
gdf.to_file(processed_data_file,driver='ESRI Shapefile')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

logger.info('Uploading original data to S3.')
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
# Find all the necessary components of the shapefile 
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
     for file in processed_data_files:
        zip.write(file, os.path.basename(file))

logger.info('Uploading processed data to S3.')
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))

'''
Upload processed data to Carto
'''

logger.info('Uploading data to Carto.')
# upload the shapefile to Carto
util_carto.upload_to_carto(processed_data_dir, 'LINK',tags=['ow'])