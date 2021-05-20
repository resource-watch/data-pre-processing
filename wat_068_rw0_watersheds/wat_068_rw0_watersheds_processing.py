import logging
import pandas as pd
import geopandas as gpd
import numpy as np
import glob
import os
import sys
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
dataset_name = 'wat_068_rw0_watersheds' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
'''
Download data and save to your data directory
Data can be downloaded from the following link:
https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACPCyoHHAQUt_HNdIbWOFF4a/HydroBASINS/standard?dl=0&subfolder_nav_tracking=1
Each folder contains the data for one of the 9 regions
Within each folder, click on the zipped folder named 'hybas_xx_lev01-12_v1c'
The download button at the top right corner will allow you to download the data to your Downloads folder
'''

# move the data from 'Downloads' into the data directory
source = os.path.join(os.getenv("DOWNLOAD_DIR"),'hybas_*_lev01-12_v1c.zip')

dest_dir = os.path.abspath(data_dir)
for file in glob.glob(source):
    logger.info(file)
    shutil.copy(file, dest_dir)

# construct a string template to specify the file name for the zipped file of given region
zip_file_template = 'data/hybas_{}_lev01-12_v1c.zip'

# make string array with the two letter codes for each region
region_ids = ['af','ar','as', 'au','eu','gr','na','sa','si']

# create an empty list to store the extracted file names
raw_namelist = []
 
logger.info('Unzipping raw data')

# unzip source data for each region using a for loop
for region_id in region_ids:
    # create object for the regional zip file using the template
    zip_file_name = zip_file_template.format(region_id) 
    # unzip source data
    with ZipFile(zip_file_name, 'r') as zip:
        # add name of exctracted file to list 
        raw_namelist.extend((zip.namelist()))
        zip.extractall(data_dir)

'''
Process the data and upload to carto 
'''

# Define object that stores which basin levels will be processed. There are 12 basin levels for each region.
include_levels = [False, False, True, True, True, True, True, True, False, False, False, False]

# Read included basin-level shapefiles into Python using a for loop
for i in range(12):
    
    # Test if the basin level should be included, using the index
    if not include_levels[i]:
        continue
   
    else:
        # create an empty list to hold the geopandas dataframes to be merged (1 per region)
        gdf_list = []
       
        # create a string of the basin level padded by zeros, using the index
        n = str(i+1).zfill(2)

        # iterate through the list of extracted file names using a for loop
        for name in raw_namelist:
            
            # read shapefiles that include the corresponding basin level as a geopandas dataframe
            if n in name and name.endswith('.shp'):
                gdf = gpd.read_file("data/" + name)
                
                # Add the geopandas dataframe to the list
                gdf_list.append(gdf) 
                
                # Add level column, pulled from the index
                level = i+1
                gdf['level'] = level
        
        # merge geopandas dataframes for basin level
        out_gdf = gpd.GeoDataFrame(pd.concat(gdf_list))

         # convert the column names to lowercase
        out_gdf.columns = [x.lower() for x in out_gdf.columns]
        
        # Generate name for processed dataset
        processed_data_file = os.path.join(data_dir, dataset_name+ '_lev'+ n + '_edit.shp')

        # save processed dataset to shapefile
        logger.debug('Creating shapefile')
        out_gdf.to_file(processed_data_file,driver='ESRI Shapefile')
    
        # Create a string of the file name of the processed data files, excluding the file extension
        out_str = processed_data_file[:-3]+'*'
        
        # Create a list of the shapefile components by grabbing files that match the string
        out_filelist = glob.glob(out_str)
        
        zipfile_list = []
        
        # Create a zipfile for the shapefile componenets
        logger.info('Zipping files for ' + processed_data_file)
       
        out_zip_dir = os.path.join(processed_data_file[:-4] + '.zip')
        with ZipFile(out_zip_dir,'w') as zip:
            for file in out_filelist:
                zip.write(file, os.path.basename(file))
                zipfile_list.append(file)

        # Upload zipfile to carto
        logger.info('Uploading processed data for ' + processed_data_file +' to Carto.')
        util_carto.upload_to_carto(out_zip_dir, 'LINK', tags=['ow'])
        
'''
Upload original data and processed data to Amazon S3 storage
'''

# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Zipping original data files.')

# Copy the raw data into a zipped file to upload to S3
raw_zip_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_zip_dir,'w') as zip:
    for file in raw_namelist:
        
        # Exclude pdfs to avoid multiple copies of the documentation file
        if not file.endswith('.pdf'):
            file_path = "data/" + file
            zip.write(file_path, os.path.basename(file_path))
   
    # Manually add the documentation file
    pdf = 'data/HydroBASINS_TechDoc_v1c.pdf'
    zip.write(pdf, os.path.basename(pdf))

logger.info('Uploading original data to S3.')

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_zip_dir, aws_bucket, s3_prefix+os.path.basename(raw_zip_dir))

logger.info('Zipping processed data files.')

# Copy the processed data into a zipped file to upload to S3
processed_zip_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_zip_dir,'w') as zip:
    for file in zipfile_list:
        zip.write(file, os.path.basename(file))

logger.info('Uploading processed data to S3.')

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_zip_dir, aws_bucket, s3_prefix+os.path.basename(processed_zip_dir))
