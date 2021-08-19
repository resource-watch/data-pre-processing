import pandas as pd
import geopandas as gpd
import urllib
import glob
import requests
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
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
# find the file paths to the shapefiles
shapefile = glob.glob(os.path.join(raw_data_file_unzipped,'glims_download_82381', 'glims_p*.shp'))
# read in the point shapefile as a geopandas dataframe
gdf_points = gpd.read_file(shapefile[0])
# read in the extent shapefile as a geopandas dataframe
gdf_extent = gpd.read_file(shapefile[1])


#rename the columns of the polygon shapefile
gdf_extent.columns = ['glacier_length' if x == 'length' else x for x in gdf_extent.columns]



# save processed dataset to shapefile
processed_data_points = os.path.join(data_dir, dataset_name +'_locations_edit.shp')
gdf_points.to_file(processed_data_points,driver='ESRI Shapefile')

processed_data_extent = os.path.join(data_dir, dataset_name +'_extent_edit.shp')
gdf_extent.to_file(processed_data_extent,driver='ESRI Shapefile')

processed_files = [processed_data_extent, processed_data_points]

'''
Upload processed data to Carto
'''
# create schema for the point dataset on Carto
CARTO_SCHEMA_pt= util_carto.create_carto_schema(gdf_points)
# create empty table for point locations on Carto
util_carto.checkCreateTable(os.path.basename(processed_data_points).split('.')[0], CARTO_SCHEMA_pt)

# create schema for the extent shapefile on Carto
CARTO_SCHEMA_extent = util_carto.create_carto_schema(gdf_extent)
# create empty table for the extent on Carto
util_carto.checkCreateTable(os.path.basename(processed_data_extent).split('.')[0], CARTO_SCHEMA_extent)

# upload the dataset to Carto and set the privacy to be 'Public with Link'
util_carto.shapefile_to_carto(os.path.basename(processed_data_points).split('.')[0], CARTO_SCHEMA_pt, gdf_points, 'LINK')
# upload the mask to Carto and set the privacy to be 'Public with Link'
util_carto.shapefile_to_carto(os.path.basename(processed_data_extent).split('.')[0], CARTO_SCHEMA_extent, gdf_extent, 'LINK')
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
# find all the necessary components of the two shapefiles
processed_pt_files = glob.glob(os.path.join(data_dir, dataset_name + '_points_edit.*'))
processed_extent_files = glob.glob(os.path.join(data_dir, dataset_name +'_extent_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
    for file in processed_pt_files + processed_extent_files:
        zip.write(file, os.path.basename(file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))