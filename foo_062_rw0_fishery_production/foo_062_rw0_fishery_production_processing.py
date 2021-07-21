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
import urllib
import numpy as np

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
dataset_name = 'foo_062_rw0_fishery_production' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''

# insert the url used to download the data from the source website
url_list = ['http://www.fao.org/fishery/static/Data/GlobalProduction_2021.1.2.zip', 'http://www.fao.org/fishery/static/Data/Aquaculture_2021.1.2.zip', 'http://www.fao.org/fishery/static/Data/Capture_2021.1.2.zip'] #check

raw_data_file = [os.path.join(data_dir,os.path.basename(url)) for url in url_list]
raw_data_file_unzipped = [file.split('.')[0] for file in raw_data_file]
processed_df = []

for url, file in zip(url_list, raw_data_file):
    # download the data from the source
    r = requests.get(url)  
    with open(file, 'wb') as f:
        f.write(r.content)

for file, unzipped in zip(raw_data_file, raw_data_file_unzipped):
    # unzip source data
    zip_ref = ZipFile(file, 'r')
    zip_ref.extractall(unzipped)
    zip_ref.close()

'''
Process the data 
'''

for file in raw_data_file_unzipped:
    # read the dataset as a pandas dataframe
    csv_data = glob.glob(os.path.join(file,'*QUANTITY.csv'))[0] 
    df_data = pd.read_csv(csv_data,encoding='latin-1')
    
    # read the country code list as a pandas dataframe
    csv_countries = glob.glob(os.path.join(file,'*COUNTRY_GROUPS.csv'))[0]
    countries_df = pd.read_csv(csv_countries, encoding='latin-1')
    
    # rename the UN Code column in the country code list to match the column in the dataset
    countries_df.rename(columns={'UN_Code':'COUNTRY.UN_CODE'}, inplace=True)

    # merge the dataframes so each country code in the dataset is matched with an ISO code and its full name
    df = pd.merge(df_data,countries_df[['COUNTRY.UN_CODE','ISO3_Code','Name_En']], on='COUNTRY.UN_CODE', how='left')
   
    # add a column to reflect the type of production measured by the value column for the dataset (ex GlobalProduction, Aquaculture, or Capture) and the variable (quantity)
    type = os.path.basename(file).split('_')[0]
    df['type'] = type + '_quantity'

    # convert the value column to a float
    df['VALUE'] = df['VALUE'].astype(float) 

    # store the processed df
    processed_df.append(df)

    # There is additional data in the Aquaculture dataset on value 
    # Process this data following the procedure above  
    if type == 'Aquaculture':
        # read the dataset as a pandas dataframe
        csv_aqua_value = glob.glob(os.path.join(file,'*VALUE.csv'))[0] 
        df_aqua_value = pd.read_csv(csv_aqua_value,encoding='latin-1')
        
        # merge the dataframes so each country code in the dataset is matched with an ISO code and its full name
        df = pd.merge(df_aqua_value,countries_df[['COUNTRY.UN_CODE','ISO3_Code','Name_En']], on='COUNTRY.UN_CODE', how='left')
   
        # add a column to reflect the type of production measured by the value column for the dataset (ex GlobalProduction, Aquaculture, or Capture) and the variable (value)
        type = os.path.basename(file).split('_')[0]
        df['type'] = type + '_value'

        # convert the value column to a float
        df['VALUE'] = df['VALUE'].astype(float)

        # store the processed df
        processed_df.append(df)

# join the three datasets
df = pd.concat(processed_df)

# rename the period column to year
df.rename(columns={'PERIOD':'year'}, inplace=True)


# pivot the table from long to short to create entires for each country and year with columns based on the 'type' of production and values which are the sum of the values for each type in a given year
table = pd.pivot_table(df, values='VALUE', index=['ISO3_Code', 'year','MEASURE'], columns=['type'], aggfunc=np.sum)

# turn all column names to lowercase
table.columns = [x.lower() for x in table.columns]

# convert Year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
table.to_csv(processed_data_file, index=True)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK', tags = ['ow'])

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
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    zipped.write(processed_data_file, os.path.basename(file))

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
