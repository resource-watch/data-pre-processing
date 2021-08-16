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
import re

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
dataset_name = 'foo_064_rw0_food_insecurity' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''

url = 'http://fenixservices.fao.org/faostat/static/bulkdownloads/Food_Security_Data_E_All_Data.zip'

# retrieve data
raw_data_file = os.path.join(data_dir, os.path.basename(url))
r = requests.get(url)  
with open(raw_data_file, 'wb') as f:
    f.write(r.content)

# unzip source data
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(data_dir)
zip_ref.close()

'''
Process the data 
'''

 # read in the data as a pandas dataframe 
df = pd.read_csv(raw_data_file.split('.')[0] + '.csv',encoding='latin-1')
    
# filter data to 
df= df[df['Item Code'] == 210091]

# filter data to countries (exclude non-aggreagted areas)
df= df[df['Area Code'] < 420]

# turn all column names to lowercase 
df.columns = [x.lower() for x in df.columns]

# replace whitespaces with underscores in column headers
df.columns = df.columns.str.replace(' ', '_')

# data is available in 3 year aggregations. Select the columns where values are aggregated in 3 year intervals.
column_list =['area', 'area_code', 'item', 'item_code', 'element', 'element_code', 'unit','y20142016', 'y20152017', 'y20162018' , 'y20172019', 'y20182020']
df = df[column_list]


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
