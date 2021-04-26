import logging
import pandas as pd
import geopandas as gpd
import json
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from datetime import datetime
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
dataset_name = 'for_021_rw1_certified_forest' #check

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# insert the url used to download the data from the source website
url = 'https://services7.arcgis.com/gp50Ao2knMlOM89z/arcgis/rest/services/AG_LND_FRSTCERT_15_2_1_2020Q2G03/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson' #check

# create path to raw data file
raw_data_file = os.path.join(data_dir, dataset_name+'.csv')
# Make request to source's API
r = requests.get(url)  
# Read response as a json object
data = r.json()
# Transform json response into a geodataframe using geopandas
normalized_data = gpd.GeoDataFrame.from_features(data['features'])
# save raw dataset to csv
normalized_data.to_csv(raw_data_file, index=False)
'''
Process data
'''
# Make a copy of normalized data to process it further
df = normalized_data.copy()
# Slice dataframe to retain only columns of interest
df = df[['indicator_code','indicator_reference','series','seriesDescription',
        'geoAreaName', 'ISO3', 'value_2000',
        'value_2005','value_2010','value_2015','value_2016',
        'value_2017','value_2018','value_2019','sources']]
# convert tables from wide form (each year is a column) to long form
df = pd.melt(df,id_vars=['indicator_code','indicator_reference','series','seriesDescription',
        'geoAreaName', 'ISO3','sources'],var_name='year', value_name='total_area_certified_ha')
# Converting total area certified from thousands of hectares to hectares
df['total_area_certified_ha'] = df['total_area_certified_ha'] *1000
# remove initial strings in year column and convert it to integer
df['year'] = df['year'].str[6:].astype('int64')
# create a new column 'datetime' to store years as datetime objects
df['datetime'] = [datetime(x, 1, 1) for x in df.year]
# convert the column names to lowercase
df.columns = [x.lower() for x in df.columns]
# replace all NaN with None
df=df.where((pd.notnull(df)), None)
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
