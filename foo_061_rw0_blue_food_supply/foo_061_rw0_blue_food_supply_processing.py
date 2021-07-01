import logging
import pandas as pd
import numpy as np
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
import re

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
dataset_name = 'foo_061_rw0_blue_food_supply' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# The data is provided as two data sets ('New' and 'Historic')
# Create a data dictionary to store the relevant information about each file including the url
data_dict= {
    'version' : [' new', 'historic'],
    'urls': ['http://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheets_E_All_Data_(Normalized).zip','http://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip'],
    'raw_files': [],
    'processed_dfs': []
  } 
 

for url in data_dict['urls']:
    # download the data from the source
    raw_data_file = os.path.join(data_dir, os.path.basename(url))
    r = requests.get(url)  
    with open(raw_data_file, 'wb') as f:
        f.write(r.content)

    # unzip source data
    raw_data_file_unzipped = raw_data_file.split('.')[0]
    zip_ref = ZipFile(raw_data_file, 'r')
    zip_ref.extractall(raw_data_file_unzipped)
    data_dict['raw_files'].append(raw_data_file_unzipped)
    zip_ref.close()

'''
Process the data 
'''
# list of marine food items and totals to include
food_list =['Aquatic Plants', 'Aquatic Animals, Others','Cephalopods','Crustaceans','Demersal Fish', 'Fish, Body Oil', 'Fish, Liver Oil', 'Marine Fish, Other', 'Meat, Aquatic Mammals', 'Molluscs, Other', 'Pelagic Fish']
total = ['Grand Total']
item_list = food_list + total 

# list of areas we want to exlude from our dataframe
# so that we only have countries and not aggregated regions
areas_list = [
    'World', 'Africa', 'Eastern Africa',
    'Middle Africa', 'Northern Africa', 'Southern Africa',
    'Western Africa', 'Americas', 'Northern America',
    'Central America', 'Caribbean', 'South America', 'Asia',
    'Central Asia', 'Eastern Asia', 'Southern Asia',
    'South-eastern Asia', 'Western Asia', 'Europe', 'Eastern Europe',
    'Northern Europe', 'Southern Europe', 'Western Europe', 'Oceania',
    'Australia and New Zealand', 'Melanesia', 'Micronesia',
    'Polynesia', 'European Union (28)', 'European Union (27)',
    'Least Developed Countries', 'Land Locked Developing Countries',
    'Small Island Developing States',
    'Low Income Food Deficit Countries',
    'Net Food Importing Developing Countries']

for file in data_dict['raw_files']:
    # read in the data as a pandas dataframe 
    df = pd.read_csv(os.path.join(file, file.split('/')[1] + '.csv'),encoding='latin-1')
    
    # filter data to food items in the list
    df= df[df['Item'].isin(item_list)]
    
    df['Type']= np.where(df['Item'].isin(food_list),'Ocean-Sourced Food', 'Grand Total')
    print(df.head)

    # filter data to the variables of interest "Food supply (kcal/capita/day)" and "Protein supply quantity (g/capita/day)"
    elements = ['664','674']
    df= df[df['Element Code'].isin(elements)]

    # filter out exculded areas 
    df = df[~df['Area'].isin(areas_list)]

    # sum the food supply values by area (country)
    df = df.groupby(['Area','Year Code', 'Type']).agg({'Area Code':'first','Element':'first', 'Value':'sum'}).reset_index()

    # store the processed df
    data_dict['processed_dfs'].append(df)

#join the new and historic datasets
df= pd.concat(data_dict['processed_dfs'])

#rename the value and year columns
df.rename(columns={'Year Code':'year'}, inplace=True)

# change whitespaces in columns
df.columns = df.columns.str.replace(' ', '_')

#Turn all column names to lowercase 
df.columns = [x.lower() for x in df.columns]

#convert Year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')

#sort the new data frame by country and year
df= df.sort_values(by=['area','datetime','type'])

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK',tags = ['ow'])

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
