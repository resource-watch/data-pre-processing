import logging
import pandas as pd
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
dataset_name = 'foo_041_rw1_non_co2_agricultural_emissions' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''

# insert the url used to download the data from the source website
url = 'http://fenixservices.fao.org/faostat/static/bulkdownloads/Emissions_Agriculture_Agriculture_total_E_All_Data_(Normalized).zip' #check

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
r = requests.get(url)  
with open(raw_data_file, 'wb') as f:
    f.write(r.content)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process the data 
'''
# read in the data as a pandas dataframe 
df = pd.read_csv(os.path.join(raw_data_file_unzipped, 'Emissions_Agriculture_Agriculture_total_E_All_Data_(Normalized).csv'),encoding='latin-1')
# filter items to only retain Agriculture total
df = df.loc[df['Item Code'] == 1711]
# filter elements to only retain Emissions (CO2eq)
df = df.loc[df['Element Code'] == 7231]
# List of areas that we want to exclude from our dataframe
# so that we only have countries and not aggregated regions
areas_lst = [
    "Africa", "Americas", "Annex I countries", "Asia", "Caribbean", 
    "Central America", "Central Asia", "Eastern Africa", "Eastern Asia", 
    "Eastern Europe", "Europe", "European Union (27)","European Union (28)", 
    "Land Locked Developing Countries","Least Developed Countries","Low Income Food Deficit Countries", 
    "Net Food Importing Developing Countries","Non-Annex I countries", "Northern Africa",
    "Northern America","Northern Europe","OECD","Small Island Developing States","South America",
    "South-eastern Asia","Southern Africa","Southern Asia","Southern Europe",
    "Western Africa","Western Asia","Western Europe","Western Sahara","World",
    "Middle Africa", "Oceania"
]
# filter dataframe based on areas list
df = df[~df['Area'].isin(areas_lst)]
# create datetime column with year information
df['datetime'] = pd.to_datetime(df.Year, format='%Y')
# convert from gigagrams to gigatonnes and store in new column
df['value_gigatonnes'] = df['Value']/1000000
# rename value to value_gigagrams
df.rename(columns={'Value':'value_gigagrams'}, inplace=True)
# change whitespaces in columns
df.columns = df.columns.str.replace(' ', '_')
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
