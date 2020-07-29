import requests
import pandas as pd
import io
import os
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
dataset_name = 'com_002_airports' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')

# insert the url used to download the data from the source website
url = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat'#check

# read in data to pandas dataframe
r = requests.get(url)
df = pd.read_csv(io.BytesIO(r.content), encoding='utf8', header=None)

# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_csv(raw_data_file, header = False, index = False)

'''
Process data
'''

# set index column of dataframe
df = df.set_index(0)

# set column names in dataframe
df.columns = ['name', 'city', 'country', 'iata', 'icao', 'latitude', 'longitude', 'altitude', 'daylight_savings_time', 'tz_database', 'time_zone', 'type', 'source']

# replace all NaN with None
df=df.where((pd.notnull(df)), None)

# replace all '\N's with None
df = df.replace({'\\N':None})

# change the data types of the 'latitude','longitude', and 'daylight_savings_time' columns to float.
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
df['daylight_savings_time'] = df['daylight_savings_time'].astype(float)

# change the data types of the 'altitude' column to integer.
df['altitude'] = df['altitude'].astype(int)

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False, encoding='utf_8_sig')

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

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
