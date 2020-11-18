import geopandas as gpd
import glob
import requests
import os
import urllib.request
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import logging

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
dataset_name = 'wat_026_rw1_wastewater_treatment_plants' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'https://edg.epa.gov/data/PUBLIC/OEI/OIC/FRS_Wastewater.zip'
# download the data from the source
r = requests.get(url)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = os.path.join(raw_data_file.split('.')[0])
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# load in the table from the geodatabase
gdb = glob.glob(os.path.join(raw_data_file_unzipped, '*.gdb'))[0]
gdf = gpd.read_file(gdb, driver='FileGDB', layer = 0, encoding='utf-8')

# rename the columns to be lowercase
gdf.columns = [x.lower() for x in gdf.columns]

# change the data type of the column 'registry_id' to integer
gdf['registry_id'] = gdf['registry_id'].astype('int64')

# reproject geometries to WGS84 (epsg 4326)
gdf = gdf.to_crs(epsg=4326)

# create a 'latitude' and 'longitude' column from the geometries in the geopandas dataframe
gdf['latitude'] = [coor.y for coor in gdf.geometry]
gdf['longitude'] = [coor.x for coor in gdf.geometry]

# remove the geometry column from the geopandas dataframe
gdf.drop(columns = 'geometry', inplace = True)

# create a path to save the processed table 
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')

# save processed dataset as a csv file
gdf.to_csv(processed_data_file, index = False)

'''
Upload processed data to Carto
'''
# create empty table for dataset on Carto
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
# Find al the necessary components of the shapefile
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
    for file in processed_data_files:
        zip.write(file, os.path.basename(file))
# Upload processed data file to S3
# adding a comment to see if my code works
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
