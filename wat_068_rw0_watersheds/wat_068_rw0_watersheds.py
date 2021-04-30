import logging
import pandas as pd
import geopandas as gpd
import numpy as np
import glob
import os
import sys
import dotenv
import requests
from collections import OrderedDict
from datetime import datetime
import dotenv
rw_env_val = os.path.abspath(os.getenv('RW_ENV'))
dotenv.load_dotenv(rw_env_val)
print(sys.path)
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
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
# using preexisting table for this dataset
dataset_name = 'wat_068_rw0_watersheds' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)


'''
Download data and save to your data directory
'''
# Use the nested file folders to navigate to stadard folder within the HydroBASINS folder
# url root folder = https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACPCyoHHAQUt_HNdIbWOFF4a/HydroBASINS/standard?dl=0&subfolder_nav_tracking=1
# For each geographic region "xx" download the zipped folder for hybas_xx_lev01-12_v1c 
# Manually move the files into the data folder (wat_068_rw0_watersheds/data)

# construct a sting template to specify the file name for given region
zip_file_template = 'data/hybas_{}_lev01-12_v1c.zip'

# make string array with the two letter codes for each region
region_ids = ['af','ar','as', 'au','eu','gr','na','sa','si']

# create an empty list to store the extracted file names
namelist = []
 
logger.info('Unzip raw data')

# unzip source data for each region using a for loop
for region_id in region_ids:
    # create object for the regional zip file using the template
    zip_file_name = zip_file_template.format(region_id) 
    # unzip source data
    with ZipFile(zip_file_name, 'r') as zip:
        # add name of exctracted file to list 
        namelist.extend((zip.namelist()))
        # zip.extractall(data_dir)

'''
Process the data and upload to carto 
'''

# Define object that stores which basin levels will be processed. There are 12 basin levels for each region.
include_levels = [True, False, False, False, False, False, False, False, False, False, False, False]


# Read included basin-level shapefiles into Python using a for loop
for i in range(12):
    
    # Test if the basin level should be included, using the index
    if not include_levels[i]:
        continue
   
    else:
        # create an empty list of regional shapefile to be merged
        file_list = []
        # create a str to match the basin level, using the index
        n = str(i+1).zfill(2)

        # iterate through the list of extracted file names using a for loop
        for name in namelist:
            
            # read shapefiles for included basin level as a gdf
            if n in name and name.endswith('.shp'):
                gdf = gpd.read_file("data/" + name)
                # Add gdf to the basin level file list
                file_list.append(gdf) 
                
                # Add level column, pulled from the index
                level = i+1
                gdf['level'] = level
                print(gdf)

                # convert the column names to lowercase
                gdf.columns = [x.lower() for x in gdf.columns]
        
        # merge gdfs for basin level
        out_gdf = gpd.GeoDataFrame(pd.concat(file_list))
        print(out_gdf)

         ## Generate name for processed dataset
        processed_data_file = os.path.join(data_dir, dataset_name+ '_lev'+ n + '_edit.shp')
        
        ## save processed dataset to shapefile
        logger.debug('Creating shapefile')
        out_gdf.to_file(processed_data_file,driver='ESRI Shapefile')

        # upload to carto
        logger.info('Uploading processed data to Carto.')
        util_carto.upload_to_carto(processed_data_file, 'LINK')
        

# # upload each shapefile corresponding to each basin level

# # some type of for loop / list comprehension to execute for each file
#         # util_carto.upload_to_carto(processed_data_file, 'LINK')

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
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
