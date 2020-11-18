import geopandas as gpd
import numpy as np
import glob
import os
import sys
import urllib.request
from collections import OrderedDict
from zipfile import ZipFile
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
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

# The purpose of this python code is to upload data from Global Mangrove Watch into the Resource Watch Carto account
# Global Mangrove Watch (GMW) provides version 2 of its data available from this website:
# https://data.unep-wcmc.org/datasets/45 by clicking the "Download" button
# GMW provides a separate shapefile containing the mangrove extents for each year for
# 1996, 2007, 2008, 2009, 2010, 2015, and 2016
# This code uploads the data from each shapefile into one table in the Resource Watch Carto account
# We also overwrite the unique ID fields of the GMW data in order to provide continuous unique ID's in the Carto table

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'for_005a_mangrove' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'http://wcmc.io/GMW_001' #check
# note - you can also download the data by year here: https://data.unep-wcmc.org/datasets/45

# download the data from the source
raw_data_file = os.path.join(data_dir, 'GMW_001_GlobalMangroveWatch.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data and upload processed data to Carto
'''

# load in the shapefiles, ordered alphabetically
shape_files = sorted(glob.glob(os.path.join(raw_data_file_unzipped,'01_Data','*.shp')))

# column names and types for data table
# column names should be lowercase
# column types should be one of the following: geometry, text, numeric, timestamp
CARTO_SCHEMA = OrderedDict([
    ('cartodb_id', 'numeric'),
    ('pxlval', 'numeric'),
    ('year', 'numeric'),
    ('the_geom', 'geometry')
])

# The unique IDs for each of the shapefiles use the same values (1,2,3,...)
# This results in duplicate unique IDs when the shapefiles are combined into one geodataframe
# Therefore, we create new unique IDs by adding the last unique ID in the table to next year's unique IDs
# Initialize a variable to track the last unique ID used in the table, so we can use it to calculate the cumulative unique ID
index_buffer = 0

# Create empty geodataframe to save combined and processed geodataframes
out_gdf = gpd.GeoDataFrame()

# Generate name for processed dataset
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')
# Create empty table for dataset on Carto
util_carto.checkCreateTable(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA)
print('Carto table created: {}'.format(os.path.basename(processed_data_file).split('.')[0]))

# Read in each shapefile into Python using a for loop
for shape_file in shape_files:
    print(shape_file)
    # Read shapefile into geodataframe
    gdf = gpd.read_file(shape_file)
    
    # Add year column, pulled from the filename
    year = os.path.basename(shape_file)
    year = int(year[4:8])
    gdf['Year'] = year

    # Convert old unique IDs to new unique IDs
    gdf['ogc_fid'] = np.arange(1,len(gdf)+1)+index_buffer
    # Save the last unique ID to the tracking variable
    index_buffer = gdf['ogc_fid'].values[-1]
    
    # Append processed geodataframe to out_gdf
    out_gdf = out_gdf.append(gdf)
    
    # Order columns
    df = gdf[['ogc_fid','pxlval','Year']]
    
    print(index_buffer)

    # Upload to Carto
    print('Uploading processed data to Carto.')
    print('Inserting new rows for shapefile: {}'.format(shape_file))
    util_carto.shapefile_to_carto(dataset_name+'_edit', CARTO_SCHEMA.keys(),CARTO_SCHEMA.values(), df)
    
#save processed dataset to shapefile
out_gdf.to_file(processed_data_file,driver='ESRI Shapefile')

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
