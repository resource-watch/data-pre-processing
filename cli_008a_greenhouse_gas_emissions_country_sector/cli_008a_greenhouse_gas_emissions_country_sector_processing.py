import dotenv
#insert the location of your .env file here:
import logging
from collections import OrderedDict
import pandas as pd
import re
import glob
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import logging
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
dataset_name = 'cli_008a_greenhouse_gas_emissions_country_sector' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.climatewatchdata.org/data-explorer

A csv file was downloaded from the explorer
after selecting the following options from menu:
    Data source: CAIT
    Countries and regions: All selected
    Sectors: All selected
    Gases: All GHG
    Start year: 1990
    End year: 2017
'''

# download the data from the source
raw_data_file = os.path.join(data_dir, 'historical_emissions.zip')

# unzip historical emissions data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''

#read in historical emissions csv data to pandas dataframe
filename=os.path.join(raw_data_file_unzipped, 'historical_emissions.csv')
df=pd.read_csv(filename)

#convert tables from wide form (each year is a column) to long form
#and pivoting sector from long to wide form (values are spread across new columns)
df_edit = pd.melt(df,id_vars=['Country', 'Sector', 'Data source', 'Gas', 'Unit'],var_name='year', value_name='value')
df_edit = df_edit.pivot_table('value', ['Country','year','Data source', 'Gas', 'Unit'], 'Sector')
df_edit = df_edit.reset_index()
#Replacing whitespaces and unwanted characters from column headers
df_edit.columns = df_edit.columns.str.replace(' ', '_')
df_edit.columns = df_edit.columns.str.replace('/', '_')
df_edit.columns = df_edit.columns.str.replace('-', '_')

#convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]

#replace all NaN with None
df_edit=df_edit.where((pd.notnull(df_edit)), None)
#Changing data types 
df_edit['year'] = df_edit['year'].astype('int64')

for col in df_edit[['agriculture', 'building', 'bunker_fuels', 'electricity_heat', 'energy','fugitive_emissions','industrial_processes','land_use_change_and_forestry', 'manufacturing_construction','other_fuel_combustion','total_excluding_lucf','total_including_lucf','transportation','waste']]:
    df_edit[col] = df_edit[col].astype('float64')
    
for col in df_edit[['country', 'data_source', 'gas', 'unit']]:
    df_edit[col] = df_edit[col].astype('str')

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'.csv')
df_edit.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK', collision_strategy='overwrite')

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
