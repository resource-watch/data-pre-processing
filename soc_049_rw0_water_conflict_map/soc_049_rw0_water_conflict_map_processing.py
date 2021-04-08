import pandas as pd
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import shutil
import logging
import glob
import urllib
from bs4 import BeautifulSoup
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
dataset_name = 'soc_049_rw0_water_conflict_map' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://www.worldwater.org/conflict/php/table-data-scraping.php?jstr={{%22region%22:%22%%22,%22conftype%22:%22%%22,%22epoch%22:%22-5000,{current_year}%22,%22search%22:%22%22}}'.format(current_year = datetime.date.today().year) #check

# fetch the data 
with urllib.request.urlopen(url) as f:
    # use BeautifulSoup to read the content as a nested data structure
    soup = BeautifulSoup(f)
    # extract all the conflict data within the "table" tag
    tableconf = soup.find( "table", {"id":"conflict"} )
    # extract each row of data as a list of strings using the 'tr' tag
    res_rows = tableconf.find_all('tr')[1:]
    
# create a dataframe from the rows, name each column in the dataframe based on the data source
df = pd.DataFrame([[x.get_text() for x in row.find_all('td')] for row in res_rows], 
                    columns = ['date', 'headline', 'conflict_type', 'region', 'description','sources', 'latitude', 'longitude', 'start_year', 'end_year'])

# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, 'data.csv')
df.to_csv(raw_data_file, header = False, index = False)

'''
Process data
'''
# remove duplicated rows based on the columns listed in the list 'subset'
df.drop_duplicates(subset=['date', 'conflict_type', 'region', 'description','sources', 'latitude', 'longitude', 'start_year', 'end_year'], inplace = True, keep='last')
     
# convert the start years to datetime objects and store them in a new column 'start_dt'
# python datetime module only support positive years (1 AD<=year<=9999 AD)
# some records in this dataset took place before 1 AD. Those dates will be stored as None
df['start_dt'] = [datetime.datetime(int(x), 1, 1) if int(x) > 1 else None for x in df.start_year]
# convert the end years to datetime objects and store them in a new column 'end_dt'
df['end_dt'] = [datetime.datetime(int(x), 1, 1) if int(x) > 1 else None for x in df.end_year]

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
