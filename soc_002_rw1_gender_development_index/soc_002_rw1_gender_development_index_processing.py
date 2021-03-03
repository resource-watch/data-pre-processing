import logging
import pandas as pd
import numpy as np
import glob
import os
import sys
import dotenv
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
dataset_name = 'soc_002_rw1_gender_development_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded from:
http://hdr.undp.org/en/indicators/137906#
'''

# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'Gender Development Index (GDI).csv'))[0]

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process the data 
'''

# read in data to pandas dataframe
df = pd.read_csv(raw_data_file, sep = ',',header=0,  skiprows=5, encoding='latin-1')
# remove rows that doesn't contain countries information
df.drop(df.tail(18).index,inplace=True)
# remove unnamed columns
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
# replace empty spaces in column names
df.columns = df.columns.str.replace(' ', '_')
# replace ".." with np.nan
df = df.replace('..', np.nan)
# remove whitespace at the beginning and end of strings
df = df.replace(to_replace="^\s+",value = '',regex=True)
# convert the column names to lowercase
df.columns = [x.lower() for x in df.columns]
# convert tables from wide form (each year is a column) to long form
df = pd.melt(df,id_vars=['hdi_rank', 'country'],var_name='year', value_name='gdi_value')
# change dtypes of columns
df['hdi_rank'] = df['hdi_rank'].astype('int64')
df['gdi_value'] = df['gdi_value'].astype('float64')
df['year'] = df['year'].astype('int64')
# create a new column 'datetime' to store years as datetime objects
df['datetime'] = [datetime(x, 1, 1) for x in df.year]
# replace all NaN with None
df=df.where((pd.notnull(df)), None)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

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
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
