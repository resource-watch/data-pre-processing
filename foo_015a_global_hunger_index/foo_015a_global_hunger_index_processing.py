import urllib.request
import tabula
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
dataset_name = 'foo_015a_global_hunger_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://www.globalhungerindex.org/pdf/en/2019.pdf' #check

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# read in data from Table 2.1 GLOBAL HUNGER INDEX SCORES BY 2019 GHI RANK, which is on page 17 of the report
df_raw=tabula.read_pdf(raw_data_file,pages=17) #check

#remove headers and poorly formatted column names (rows 0, 1)
df_raw=df_raw.iloc[2:]

#get first half of table (columns 1-5, do not include rank column)
df_a=df_raw.iloc[:, 1:6]
#name columns
col_names = ["Country", "2000", "2005", "2010", "2019"] #check
df_a.columns = col_names
#get second half of table (columns 7-11, do not include rank column) and drop empty rows at end
df_b=df_raw.iloc[:, 7:12].dropna(how='all')
#name columns
df_b.columns = col_names

#combine first and second half of table
df = pd.concat([df_a, df_b], ignore_index=True, sort=False)

# clean the dataframe
# replace <5 with 5
df= df.replace('<5', 5)
#replace — in table with None
df = df.replace({'—': None})

#convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
df_long = pd.melt (df, id_vars= ['Country'] , var_name = 'year', value_name = 'hunger_index_score')

#convert year column from object to integer
df_long.year=df_long.year.astype('int64')
#convert hunger_index_score column from object to number
df_long.hunger_index_score = df_long.hunger_index_score.astype('float64')
#replace NaN in table with None
df_long=df_long.where((pd.notnull(df_long)), None)

#add rows for countries with insuffient data, but significant concern, as noted here:
# https://www.globalhungerindex.org/results.html#box-2-1

#add a column to our dataframe to store this flag - it will be False for all the countries already in our table
df_long['sig_concern'] = False

#make a list of countries for which there is insuffient data, but significant concern
sig_concern = ['Burundi', 'Comoros', 'Democratic Republic of Congo', 'Eritrea', 'Libya', 'Papua New Guinea', 'Somalia',
               'South Sudan', 'Syrian Arab Republic']

#add a new row to the dataframe for each of these countries, there will be no index score, but we will mark the flag as True
for country in sig_concern:
    row = [country, 2019, None, True]
    df_long = df_long.append(pd.Series(row, index=df_long.columns), ignore_index=True)

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_long.to_csv(processed_data_file, index=False)


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