import requests
import pandas as pd
import os
import sys
import io
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import glob
import shutil
import logging
import datetime

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
dataset_name = 'soc_004_rw1_human_development_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Data can be downloaded at the following link:
    http://hdr.undp.org/en/indicators/137506#
Above the data table, you will see a 'Download Data' button
Once you click this button, the data will be downloaded as a csv file to your Downloads folder.
'''
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'Human Development Index (HDI).csv'))[0]

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process data
'''
# read the data as a pandas dataframe 
df = pd.read_csv(raw_data_file)  

# remove empty columns from the dataframe
df.dropna(axis = 1, how = 'all', inplace = True)

# remove empty rows and rows that only contain metadata
df.dropna(axis = 0, how = 'any', inplace = True)

# replace the '..' in the dataframe with None 
df.replace('..', 'None', inplace = True)

# convert the data type of the column 'HDI Rank' to integer
df['HDI Rank'] = pd.to_numeric(df['HDI Rank'], errors='coerce')
df['HDI Rank'] = df['HDI Rank'].astype('Int32')

# convert the dataframe from wide to long format 
# so there will be one column indicating the year and another column indicating the index
df = df.melt(id_vars = ['HDI Rank', 'Country'])

# rename the 'variable' and 'value' columns created in the previous step to 'year' and 'yr_data'
df.rename(columns = { 'variable': 'year', 'value':'yr_data'}, inplace = True)

# convert the data type of the 'year' column to integer 
df['year'] = df['year'].astype('int')

# convert the years in the 'year' column to datetime objects and store them in a new column 'datetime'
df['datetime'] = [datetime.datetime(x, 1, 1) for x in df.year]

# convert the data type of column 'yr_data' to float 
df['yr_data'] = pd.to_numeric(df['yr_data'], errors='coerce')

# rename the column 'HDI Rank' to 'hdi_rank' since space within column names is not supported by Carto 
# rename the column 'Country' to 'country_region' since the column contains both countries and regions 
df.rename(columns = { 'HDI Rank': 'hdi_rank', 'Country':'country_region'}, inplace = True)

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
# adding a comment to see if my code works
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
