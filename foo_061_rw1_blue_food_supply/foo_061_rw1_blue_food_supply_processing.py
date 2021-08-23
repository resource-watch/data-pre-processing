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
import shutil

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
dataset_name = 'foo_061_rw1_blue_food_supply' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# The data is provided as two data sets ('New' and 'Historic')
# Create a data dictionary to store the relevant information about each file 
    # version: version of data (string)
    # url: url to retrieve data (string)
    # raw_data_file: empty list for raw data files (list)
    # processed_dfs: empty list for processed dataframes (list)

data_dict= {
    'version' : [' new', 'historic'],
    'urls': ['http://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheets_E_All_Data_(Normalized).zip','http://fenixservices.fao.org/faostat/static/bulkdownloads/FoodBalanceSheetsHistoric_E_All_Data_(Normalized).zip'],
    'raw_data_file': [],
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
    data_dict['raw_data_file'].append(raw_data_file_unzipped)
    zip_ref.close()

# Copy item aliasing sheet into the data directory
source = os.path.join(os.getenv("OCEANWATCH_DATA_DIR"),'FBS_item_category_analysis.xlsx')
dest_dir = os.path.abspath(data_dir)
shutil.copy(source, dest_dir)

'''
Process the data 
'''
# list of areas we want to exclude from our dataframe
# so that we only have countries and not aggregated regions
areas_list = ['Africa', 'Eastern Africa',
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
    'Net Food Importing Developing Countries','Australia & New Zealand', 
    'Belgium-Luxembourg', 'China', 'Czechoslovakia','Ethiopia PDR', 
    'European Union', 'Netherlands Antilles (former)', 'Serbia and Montenegro', 
    'South-Eastern Asia', 'Sudan (former)', 'USSR', 'Yugoslav SFR']

for file in data_dict['raw_data_file']:
    # read in the data as a pandas dataframe 
    df = pd.read_csv(os.path.join(file, file.split('/')[1] + '.csv'),encoding='latin-1')
    # read in the category alias sheet as a dataframe
    alias = pd.read_excel(os.path.join(data_dir, 'FBS_item_category_analysis.xlsx'))
    # match the items in the food balance sheet with their assigned category in the category alias sheet
    df = pd.merge(df, alias[['Item Code','Analysis Category','Product', 'Parent']], on='Item Code', how='left')
    
    # filter out items that were not matched to a category alias
    df= df[df['Analysis Category'].notnull()]

    # filter data to the element "Protein supply quantity (g/capita/day)"
    elements = [674]
    df= df[df['Element Code'].isin(elements)]

    # filter out excluded areas 
    df = df[~df['Area'].isin(areas_list)]

    # create a data frame for the 4th level (items)
    df_item = df[df['Item'] != 'Grand Total']
    df_item['Size'] = df_item['Value']

    # create a data fram for the 3rd level (groups)
    df_group = df_item.groupby(['Area','Year Code', 'Parent']).agg({'Area Code':'first', 'Analysis Category':'first', 'Element': 'first', 'Value':'sum', 'Unit': 'first'}).reset_index()
    df_group.rename(columns={'Parent':'Item'}, inplace=True)
    df_group['Parent'] = df_group['Analysis Category']

    # create a data frame for the 2nd level (categories) 
    df_category = df_item.groupby(['Area','Year Code', 'Analysis Category']).agg({'Area Code':'first', 'Element': 'first', 'Value':'sum', 'Unit': 'first'}).reset_index()
    df_category['Parent'] = 'Grand Total'
    df_category['Item']=df_category['Analysis Category']
    
    #create a data frame for the 1st level (total)
    df_total = df[df['Item'] == 'Grand Total']
    df_total['Parent'] = None
    df_total['Size'] = None

    # combine dfs
    df= pd.concat([df_total, df_category, df_group, df_item])

    # store the processed df
    data_dict['processed_dfs'].append(df)

# join the new and historic datasets
df= pd.concat(data_dict['processed_dfs'])

# rename the value and year columns
df.rename(columns={'Year Code':'year'}, inplace=True)

# replace whitespaces with underscores in column headers
df.columns = df.columns.str.replace(' ', '_')

# turn all column names to lowercase 
df.columns = [x.lower() for x in df.columns]

# remove duplicate columns
df = df.loc[:,~df.columns.duplicated()]

# convert Year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')

# convert value column to a float
df['value'] = df['value'].astype('float64')

# sort the new data frame by country and year
df= df.sort_values(by=['area','year','analysis_category', 'product', 'item'])

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
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
     raw_data_files = data_dict['raw_data_file']
     for raw_data_file in raw_data_files:
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
