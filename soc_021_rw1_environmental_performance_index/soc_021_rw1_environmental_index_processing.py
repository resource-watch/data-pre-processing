import os
import urllib
import pandas as pd
from zipfile import ZipFile
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
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
dataset_name = 'soc_021_rw1_environmental_performance_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://epi.yale.edu/downloads/epi2020results20200604.csv'

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

# download the interpretation of all the indicator abbreviations from the source website 
url_indicator = 'https://epi.yale.edu/downloads/epi2020indicatortla20200604.csv'
indicator_file = os.path.join(data_dir, os.path.basename(url_indicator))
urllib.request.urlretrieve(url_indicator, indicator_file)

'''
Process data
'''
# read in the csv file of the data as Dataframe
df = pd.read_csv(raw_data_file)

# read in the csv file of the indicator abbreviations as dataframe 
df_indicator = pd.read_csv(indicator_file)

# replace the special characters in the 'Short name' column with underscores and 
# convert the strings to lowercase
df_indicator['Short name'] = [x.replace(' ', '_').replace('.', '_').replace('-', '_').
                              lower() for x in df_indicator['Short name']]
df_indicator['Short name'] = [x.replace("(nat'l)", 'national').replace("(global)", 'global').
                              replace('_&_', '_') for x in df_indicator['Short name']]

# create a dictionary to store each abbreviation and the corresponding name 
abbre_dict = {df_indicator['Abbreviation'][i]: df_indicator['Short name'][i] for i in range(len(df_indicator['Short name']))} 

# replace the abbreviations in the column names with full names of indicators 
rename_col = []
for col in df.columns: 
    for key, value in abbre_dict.items():
        col = col.replace(key, value).replace('.', '_')
    rename_col.append(col)
df.columns = rename_col 

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

