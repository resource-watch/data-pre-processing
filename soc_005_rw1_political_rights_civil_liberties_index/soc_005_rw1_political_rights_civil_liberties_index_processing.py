import pandas as pd
import requests
import io
import sys
import os
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
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
dataset_name = 'soc_005_rw1_political_rights_civil_liberties_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url= 'https://freedomhouse.org/sites/default/files/2020-02/2020_Aggregate_Category_and_Subcategory_Scores_FIW_2003-2020.xlsx'

# download the data from the source
r = requests.get(url)
# read in data as a pandas dataframe
df = pd.read_excel(io.BytesIO(r.content), encoding='utf8', header=0, sheet_name='FIW06-20')

# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_excel(raw_data_file, header = False, index = False)

'''
Process data
'''
# remove empty columns
df.dropna(axis = 1, how = 'all', inplace = True)

# change the names of column 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'CL', 'PR', and 'Total'
# to match the column names in the previous Carto table 
df.rename(columns = {'A': 'a_aggr',
                     'B': 'b_aggr',
                     'C': 'c_aggr',
                     'D': 'd_aggr',
                     'E': 'e_aggr',
                     'F': 'f_aggr',
                     'G': 'g_aggr',
                     'CL': 'cl_aggr',
                     'PR': 'pr_aggr',
                     'Total': 'total_aggr'},
          inplace = True)						

# rename the 'country/territory' and 'c/t?' columns to replace characters unsupported by Carto with underscores
df.rename(columns = {'Country/Territory': 'country_territory',
                     'C/T?': 'c_t_'}, inplace = True)	

# convert the column names to lowercase letters and replace spaces with underscores
df.columns = [x.lower().replace(' ', '_') for x in df.columns]

# since the data cover the development in the year before they are released
# create a new column 'year_reviewed' to indicate the year of development the data are based on 
df['year_reviewed'] = [x-1 for x in df.edition]

# convert the years in the 'year_reviewed' column to datatime objects and store them in a new column 'datetime'
df['datetime'] = [datetime.datetime(x, 1, 1) for x in df.year_reviewed]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index = False)

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
