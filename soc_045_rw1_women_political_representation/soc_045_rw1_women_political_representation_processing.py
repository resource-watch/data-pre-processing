import logging
import pandas as pd
import numpy as np
import glob
import os
import sys
import requests
from datetime import datetime
import dotenv
#insert the location of your .env file here:
dotenv.load_dotenv('/home/eduardo/Documents/RW_github/cred/.env')
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
dataset_name = 'soc_045_rw1_women_political_representation' #check

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://stats.oecd.org/Index.aspx?DataSetCode=GIDDB2019
Above the table, there is a 'export' button that will lead to a dropdown menu containing different export options.
Once you select 'Text file (CSV)' from the menu, a new window will occur and allow you to download the data as a csv file to your Downloads folder.
'''
# download the data from the source
logger.info('Start processing')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'GIDDB2019_05032021222441244.csv'))[0]
# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

# read in data to pandas dataframe
df = pd.read_csv(raw_data_file)
'''
Process data
'''
# remove 'TIME' column because it is identical to the 'year' column
# remove columns with filled with empty strings 
df = df.drop(columns = ['TIME','Flag Codes', 'Flags','Variable'])

# reformat the dataframe so each variable becomes a new column
pivoted = pd.pivot_table(df, index = ['REGION','Region','LOCATION', 'Country','INC','Income','Year'], columns = 'VAR', values = 'Value').reset_index()
pivoted.rename(columns={'REGION': 'REG'}, inplace=True)
# convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'
pivoted['datetime'] = [datetime(x, 1, 1) for x in pivoted.Year]
# Drop duplicates so that only one row per country remains
pivoted = pivoted[pivoted.Income != 'All income groups']
pivoted = pivoted[pivoted.Region != 'All regions']
#Turn all column names to lowercase
pivoted.columns = [x.lower() for x in pivoted.columns]
pivoted = pivoted.reset_index(drop=True)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
pivoted.to_csv(processed_data_file, index=False)

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

