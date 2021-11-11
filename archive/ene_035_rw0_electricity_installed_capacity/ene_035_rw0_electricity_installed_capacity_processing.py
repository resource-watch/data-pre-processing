import os
import pandas as pd
from zipfile import ZipFile
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import datetime 
import requests
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
dataset_name = 'ene_035_rw0_electricity_installed_capacity' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to find the series ids of the data 
url = 'http://api.eia.gov/category/?api_key={}&category_id=2134409'.format(os.environ.get('EIA_KEY'))#check

# fetch the information of all series of data in this category from the API 
r = requests.get(url)
series = r.json()['category']['childseries']

# store the names and ids of the child series in a list of dictionaries
ids = [{'country': ', '.join(child['name'].split(', ')[1:-1]), 'series_id': child['series_id']} for child in series]

# create an empty dataframe to store data 
df = pd.DataFrame()
# loop through each series id
for id in ids:
    # construct the API call to fetch data from the series
    data_url = 'http://api.eia.gov/series/?api_key={}&series_id={}'.format(os.environ.get('EIA_KEY'),
                                                                           id['series_id'])
    logging.info('Fetching data for {}'.format(id['country']))
    # extract the data from the response 
    data = requests.get(data_url).json()['series'][0]
    # create a dataframe with the column 'year' and 'yr_data' from the data 
    df_country = pd.DataFrame({'year':[x for [x,y] in data['data']], 'yr_data': [y for [x,y] in data['data']]})
    # create a new column 'country' to store the country information 
    df_country['country'] = id['country']
    # create a new column 'geography' to store the code of the country/region
    df_country['geography'] = data['geography']
    # create a new column 'unit' to store the units
    df_country['unit'] = data['units']
    # concat the data frame to the larger dataframe created before the loop
    df = pd.concat([df, df_country], ignore_index=True)

# create a file path to save the raw data 
raw_data_file = os.path.join(data_dir, 'data.csv')
# save the raw data as a csv file 
df.to_csv(raw_data_file, index = False)

'''
Process data
'''
# reorder the dataframe 
df = df[['country', 'geography', 'year', 'unit', 'yr_data']]

# remove duplicated rows 
df.drop_duplicates(inplace=True)

# subset the dataframe to remove the data of larger regions that consist of multiple geographies 
df = df[df.geography.apply(lambda x: ('+' not in x) & (x != 'WLD'))]
# remove OPEC - South America since it's a duplicate of Venezuela
df = df[df.country != 'OPEC - South America']

# convert the data type of 'year' column to int 
df['year'] = df['year'].astype(int)

# create a column to store the year information as datetime objects 
df['datetime'] = [datetime.datetime(x, 1, 1) for x in df['year']]

# remove rows with no data 
df = df.loc[df.yr_data != '--']

# convert the data type of the column 'yr_data' to float
df.yr_data = df.yr_data.astype(float)

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
