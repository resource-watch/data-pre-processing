import pandas as pd
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import urllib
from zipfile import ZipFile
import datetime
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
dataset_name = 'cit_022_road_traffic_death_rates' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://apps.who.int/gho/athena/data/GHO/RS_196,RS_198?filter=COUNTRY:*&x-sideaxis=COUNTRY&x-topaxis=GHO;YEAR&profile=crosstable&format=csv'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'data.csv')
urllib.request.urlretrieve(url, raw_data_file)
'''
Process data
'''
# read in csv file as Dataframe
df=pd.read_csv(raw_data_file, header=1) # selecting 2nd row as the column names
#rename all the columns
df.rename(columns={df.columns[0]:'country'}, inplace=True)
df.rename(columns={df.columns[1]:'estimated_number_of_road_traffic_deaths_data'}, inplace=True)
df.rename(columns={df.columns[2]:'death_rate_per_100000'}, inplace=True)
# get the Estimated number of road traffic deaths by splitting
# 'estimated_number_of_road_traffic_deaths_data' column on '[' and getting the first
# element from the split. Store the second element from split to a new column 'bounds'
df[['estimated_number_of_road_traffic_deaths_data','bounds']]=df['estimated_number_of_road_traffic_deaths_data'].str.split('[', expand=True)
# create a new column for lower bound of estimated number of road traffic deaths
# split the values from column 'bounds' on '-' and insert the first element
# to the column 'estimated_lower_bound'
# replace values in the column 'bounds' with second element from this split
df[['estimated_lower_bound','bounds']]=df['bounds'].str.split('-', expand=True)
# rename 'bounds' column to 'estimated_upper_bound'
df.rename(columns={'bounds': 'estimated_upper_bound'}, inplace=True)
# remove unnecessary character ']' from the end of each row in 'estimated_upper_bound' column
df['estimated_upper_bound'] = df['estimated_upper_bound'].str[:-1]
# add a column for datetime with January 1, 2016 for every row
df['datetime'] = datetime.datetime(2016, 1, 1)
# rearrange the column names
df = df[['country', 'datetime', 'death_rate_per_100000','estimated_lower_bound',
         'estimated_number_of_road_traffic_deaths_data','estimated_upper_bound']]
# there are some rows which has empty spaces in between numbers in the
# 'estimated_number_of_road_traffic_deaths_data' column. remove those empty spaces
df['estimated_number_of_road_traffic_deaths_data'] = df['estimated_number_of_road_traffic_deaths_data'].str.replace(' ', '')
#save processed dataset to csv
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
