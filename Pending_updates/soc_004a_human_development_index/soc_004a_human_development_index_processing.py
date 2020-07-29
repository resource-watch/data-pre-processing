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
dataset_name = 'soc_004a_human_development_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
   
'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://hdr.undp.org/sites/default/files/hdro_statistical_data_tables_1_15_d1_d5.xlsx' #check

# read in data to pandas dataframe
r = requests.get(url)
df = pd.read_excel(io.BytesIO(r.content), encoding='utf8')

# save unprocessed source data
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_excel(raw_data_file, header=False, index=False)

'''
Process data
'''
# store the information in the metadata rows 
titles = list(df.iloc[3].fillna(''))
units = list(df.iloc[4].fillna(''))
years = list(df.iloc[5].fillna(''))
# generate headers for the data columns
headers = []
for title, year, unit in zip(titles, years, units):
    # remove any extra whitespace from year
    # add space before year because Carto column name cannot begin with number
    year_edited = ' ' + year.strip()
    # remove any parentheses and extra whitespace from title
    # add space before title because it will follow year
    title_edited = ' ' + title.strip().replace('(', '').replace(')', '')
    # remove any parentheses and extra whitespace from unit
    # replace $ with dollars because Carto cannot have symbols in headers
    # add space before unit because it will follow title
    unit_edited = ' ' + unit.strip().replace('(', '').replace(')', '').replace('$', 'dollars')
    # join year, title, unit into one string and replace spaces with underscores
    headers.append((year_edited + title_edited + unit_edited).strip().replace(' ', '_'))

# drop metadata rows
df = df[7:]
# assign correct headers to the columns 
df.columns = headers
# remove unnamed columns because they contain flags to reference footers that are no longer in the table, or contain no values at all
columns = [c for c in df.columns if len(c) > 1]
df = df[columns].reset_index(drop=True)

# delete rows that do not contain country information (identified by an empty 'HDI rank' column)
df = df.dropna(subset=['HDI_rank'])

# replace all '..', which is used to mark no-data, with None
df = df.replace({'..':None})

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
