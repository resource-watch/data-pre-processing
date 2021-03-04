import logging
import pandas as pd
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from bs4 import BeautifulSoup
import urllib
import requests
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
dataset_name = 'soc_023_rw1_fragile_states_index' #check

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# Retrieve the html page from source
req = urllib.request.Request("https://fragilestatesindex.org/excel/", headers={'User-Agent': 'Mozilla/5.0'})
html_page = urllib.request.urlopen(req)
soup = BeautifulSoup(html_page, "lxml")
# Find all the links in html document
links = []
for link in soup.findAll('a'):
    links.append(link.get('href'))
# Drop duplicated links
links = list(set(links))
# Create list containing only links of xlsx files
url_list = []
for link in links:
    if link.endswith(('.xlsx')):
        url_list.append(link)
# Create file paths where the excel files will be stored
raw_data_file = [os.path.join(data_dir,os.path.basename(url)) for url in url_list]
# Download data from source
for index,element in enumerate(url_list):
    res = requests.get(element, headers={'User-Agent': 'Mozilla/5.0'})
    res.raise_for_status()
    # write the file to data directory
    with open(raw_data_file[index], 'wb') as f:
        f.write(res.content)

# Go through data directory and append xlsx files into a list
# Then concatenate the content of the list in a dataframe
df_list = []
for file in raw_data_file:
    df = pd.read_excel(file)
    df_list.append(df)
df = pd.concat(df_list, ignore_index=True)

# Delete prefixes in columns that have them
df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.replace(':', '')
#Turn all column names to lowercase
df.columns = [x.lower() for x in df.columns]
# replace all NaN with None
df = df.where((pd.notnull(df)), None)

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
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))
logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file)) 
        
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
