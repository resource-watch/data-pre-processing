import logging
import pandas as pd
import numpy as np
import glob
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import requests
from zipfile import ZipFile
import shutil

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
dataset_name = 'ocn_023_rw1_marine_protection' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

The data was downloaded manually from https://stats.oecd.org/Index.aspx?DataSetCode%3DPROTECTED_AREAS 
To download the data, hover over the export menu at the top of the page. Select "Text file (CSV)" to dowload the data to your downloads folder.
'''

# Grab each file with the corresponding names from the Downloads folder
source = glob.glob(os.path.join(os.getenv("DOWNLOAD_DIR"),'PROTECTED_AREAS_*.csv'))[0]
# create a path to the raw data file 
raw_data_file = os.path.join(data_dir, os.path.basename(source))
# create a path to the data directory
dest_dir = os.path.abspath(data_dir)
# copy the file to the data directory
logger.info(source)
shutil.copy(source, dest_dir)

'''
Process the data 
'''

# read in the data as a pandas dataframe 
df = pd.read_csv(raw_data_file,encoding='latin-1')

# rename the column 'COUNTRY' to 'iso'
df.rename(columns = {'ï»¿"COU"': 'iso'}, inplace = True)

# remove duplicate and blank columns 
column_list = ['iso', 'Country', 'Designation', 'Domain', 'Measure', 
        'Calculation method', 'Scope', 'Year', 'Unit Code', 'Unit',
        'Value']

df = df[column_list]

# turn all column names to lowercase 
df.columns = [x.lower() for x in df.columns]

# convert time column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK',tags = ['ow'])

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
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file)) 
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
