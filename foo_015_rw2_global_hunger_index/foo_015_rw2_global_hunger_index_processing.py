import urllib.request
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
dataset_name = 'foo_015_rw2_global_hunger_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://www.globalhungerindex.org/xlsx/2021.xlsx' #check

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# read in data from TABLE 1.1 Global Hunger Index Scores By 2021 GHI Rank
df_raw = pd.read_excel(raw_data_file) #check

# remove headers and poorly formatted column names (rows 0, 1)
df_raw = df_raw.iloc[2:-2]

# get second half of table (columns 3-7, do not include rank column)
df = df_raw.iloc[:, 2:8]
# name columns
col_names = ["country", "2000", "2006", "2012", "2021"] #check
df.columns = col_names

# clean the dataframe
# replace <5 with 5
df = df.replace('<5', 5)
# replace — in table with None
df = df.replace({'—': None})
# remove rows with a range instead of an index
df = df[df["2021"].str.contains("-") != False]

# convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
df_long = pd.melt (df, id_vars= ['country'] , var_name = 'year', value_name = 'hunger_index_score')

# convert year column from object to integer
df_long.year = df_long.year.astype('int64')
# convert hunger_index_score column from object to number
df_long.hunger_index_score = df_long.hunger_index_score.astype('float64')
# replace NaN in table with None
df_long = df_long.where((pd.notnull(df_long)), None)

# add rows for countries with incomplete data, but significant concern, as noted here:
# https://www.globalhungerindex.org/designations.html

# add a column to our dataframe to store this flag - it will be False for all the countries already in our table
df_long['incomplete_data'] = False

# make a list of countries for which there is insuffient data, but significant concern
incomplete_data = ['Moldova', 'Tajikistan', 'Guinea', 'Guinea-Bissau', 'Niger', 'Uganda', 'Zambia', 'Zimbabwe', 'Burundi', 'Comoros', 
                   'South Sudan', 'Syrian Arab Republic', 'Bahrain', 'Bhutan', 'Equatorial Guinea', 'Eritrea', 'Libya', 'Maldives', 'Qatar']

# add a new row to the dataframe for each of these countries, there will be no index score, but we will mark the flag as True
for country in incomplete_data:
    row = [country, 2021, None, True]
    df_long = df_long.append(pd.Series(row, index = df_long.columns), ignore_index = True)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_long.to_csv(processed_data_file, index = False)


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
