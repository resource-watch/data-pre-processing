import geopandas as gpd
import glob
import os
import shutil
from shapely.geometry import Polygon
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
dataset_name = 'bio_004a_coral_reef_locations'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://wcmc.io/WCMC_008'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'WCMC008_CoralReefs2018_v4.zip')
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
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, '14_001_WCMC008_CoralReefs2018_v4', '01_Data', '*Py_v4.shp'))[0]
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
Create a mask for the data
To create a mask for the dataset, you need to first create a 10km buffer around each coral reef polygon
Considering the time and computation power needed to complete this operation, 
we recommend you create the buffer in Google Earth Engine and export it as a shapefile to Google Drive
(the code used to do this is provided in the README for this pre-processing)
You will then be able to download the buffer shapefile from your Google Drive
'''
# download the shapefile from the Google Drive
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'drive*.zip'))[0]
# Move this file into your data directory
buffer_zipped = os.path.join(data_dir, os.path.basename(download))
shutil.move(download, buffer_zipped)

# unzip the buffer data 
buffer_unzipped = buffer_zipped.split('.')[0]
zip_ref = ZipFile(buffer_zipped, 'r')
zip_ref.extractall(buffer_unzipped)
zip_ref.close()

# read the shapefile that contains 10km buffer around the dataset as a geopandas data frame
gdf_buffer = gpd.read_file(os.path.join(buffer_unzipped, dataset_name+'_buffer.shp'), encoding='latin-1')

# create a new field 'dissolve_id' 
gdf_buffer['dissolve_id'] = 1
# dissolve the buffered polygons into a single polygon
gdf_dis = gdf_buffer.dissolve(by='dissolve_id')

# we only need the geometry of the buffered coral reef polygon to create a mask 
# therefore we remove columns other than the 'geometry' column and reset the index 
gdf_dis = gpd.GeoDataFrame(gdf_dis.geometry).reset_index(drop = True)

# create a polygon that covers the entire world 
polygon = Polygon([(-180, 90), (-180, -90), (180, -90), (180, 90)])
# convert the polygon into a geopandas dataframe 
poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=gdf_buffer.crs)

# create a mask by finding the difference between the world polygon and the buffered coral reef polygon
gdf_mask = gpd.overlay(poly_gdf, gdf_dis, how='difference')
# assign the correct headers to the mask dataframe 
gdf_mask.columns = ['cartodb_id', 'geometry']

# convert the data type of the column 'cartodb_id' in the mask dataframe to integer
gdf_mask.cartodb_id = gdf_mask.cartodb_id.astype(int)
# export the mask as a shapefile 
processed_data_mask = os.path.join(data_dir, dataset_name+'_mask.shp')
gdf_mask.to_file(processed_data_mask, driver='ESRI Shapefile')

'''
Upload processed data to Carto
'''

# create schema for dataset on Carto
CARTO_SCHEMA_data = util_carto.create_carto_schema(gdf)
# create empty table for dataset on Carto
util_carto.checkCreateTable(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA_data)

# create schema for the mask on Carto
CARTO_SCHEMA_mask = util_carto.create_carto_schema(gdf_mask)
# create empty table for the mask on Carto
util_carto.checkCreateTable(os.path.basename(processed_data_mask).split('.')[0], CARTO_SCHEMA_mask)

# upload the dataset to Carto and set the privacy to be 'Public with Link'
util_carto.shapefile_to_carto(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA_data, gdf, 'LINK')
# upload the mask to Carto and set the privacy to be 'Public with Link'
util_carto.shapefile_to_carto(os.path.basename(processed_data_mask).split('.')[0], CARTO_SCHEMA_mask, gdf_mask, 'LINK')

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
# find all the necessary components of the two shapefiles
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
processed_mask_files = glob.glob(os.path.join(data_dir, dataset_name +'_mask.*'))
with ZipFile(processed_data_dir,'w') as zip:
    for file in processed_data_files + processed_mask_files:
        zip.write(file, os.path.basename(file))
        
# Upload processed data file to S3
# adding a comment to see if my code works
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
