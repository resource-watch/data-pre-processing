import pandas as pd
import urllib
from bs4 import BeautifulSoup
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
dataset_name = 'for_018_rw1_bonn_challenge_restoration_commitment' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Scrape data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to scrape the data from the source website
url = 'https://www.bonnchallenge.org/pledges'

# scrape the data from the source website 
with urllib.request.urlopen(url) as f:
    # use BeautifulSoup to read the content as a nested data structure
    soup = BeautifulSoup(f)
    # extract all the data within the class "view__content-inner"
    table = soup.find("div", class_='view__content-inner')
    # extract each row of data as a list of strings using the 'content__body' class
    res_rows = soup.find_all("div", class_ = 'content__body')
# split strings using newline delimiter and convert them to a pandas dataframe  
df = pd.DataFrame([[x for x in row.get_text().split('\n') if x != ''] for row in res_rows],
                    columns = ['country', 'region', 'pledged_area'])
    
# export the pandas dataframe to a csv file
raw_data_file = os.path.join(data_dir, 'data.csv')
df.to_csv(raw_data_file, index = False)

'''
Process data
'''
# create a new column 'unit' to store the unit of the pledged areas 
df['unit'] = 'million hectare'

# remove 'hectare' from all the entries in the column 'pledged_area'
df['pledged_area'] = [x.replace('hectares', '') for x in df.pledged_area]

# Convert the data type of the 'pledged_area' column to integer
df = df.astype({'pledged_area': int})

# convert the values in the column 'pledged_area' to be in million hectares
df['pledged_area'] = [x/1000000 for x in df.pledged_area]

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