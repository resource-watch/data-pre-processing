import logging
import numpy as np
import pandas as pd
from datetime import datetime
import glob
import os
import sys
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
# using preexisting table for this dataset
dataset_name = 'soc_035_rw1_land_deals' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://landmatrix.org/list/deals

A xlsx file was downloaded from the explorer
after selecting the following options from the filter menu:

Deal size: 200 hectares
Negotiation status: Concluded
'''
# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'export.xlsx'))[0]

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process data
'''
# read "deals" sheet in xlsx file
df_edit =  pd.read_excel(raw_data_file, 'Deals')
# replace spaces and special characters in column headers with '_" 
df_edit.columns = df_edit.columns.str.replace(' ', '_')
df_edit.columns = df_edit.columns.str.replace('/', '_')
df_edit.columns = df_edit.columns.str.replace('-', '_')
df_edit.columns = df_edit.columns.str.replace(':', '_')


# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]

# select columns that we want to store in Carto table
df_edit = df_edit[['deal_id', 'is_public', 'deal_scope','deal_size','target_country','current_negotiation_status', 
                   'intention_of_investment','top_parent_companies','negotiation_status']]
# Split negotiation status column to obtain year of negotiation
df_edit['negotiation_status_year'] = df_edit['negotiation_status'].map(lambda x: x.split('#')[0])
df_edit['negotiation_status_year'] = df_edit['negotiation_status_year'].map(lambda x: x.split('-')[0])

# Convert negotiation year column to integeer
df_edit['negotiation_status_year'] = pd.to_numeric(df_edit['negotiation_status_year'], errors='coerce').fillna(np.nan, downcast='infer').astype('Int64')
# Convert negotiation year column to datetime
df_edit['negotiation_status_year']  = pd.to_datetime(df_edit['negotiation_status_year'] , format='%Y', errors='coerce')
# replace all NaT with None
df_edit=df_edit.replace({pd.NaT: None})
# replace all NaN with None
df_edit=df_edit.where((pd.notnull(df_edit)), None)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_edit.to_csv(processed_data_file, index=False)

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
