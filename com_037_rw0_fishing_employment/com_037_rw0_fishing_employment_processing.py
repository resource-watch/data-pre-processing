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
import gzip 

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
dataset_name = 'com_037_rw0_fishing_employment' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

The data was downloaded manually from https://ilostat.ilo.org/data/# 
Scroll to the bottom of the page and click the ".gz" button for 
- Level 1: "Employment by sex and economic activity (thousands) | Annual" [Code: EMP_TEMP_SEX_ECO_NB_A] and
- Level 2: "Employment by sex and economic activity - ISIC level 2 (thousands) | Annual" [Code: EMP_TEMP_SEX_EC2_NB_A]
'''

# Create a data dictionary to store the relevant information about each file 
    # raw_data_file: empty list for raw data files (list)
    # processed_dfs: empty list for processed dataframes (list)

data_dict= {
    'raw_data_file': [],
    'processed_dfs': []
  } 

# move the data from 'Downloads' into the data directory
source = os.path.join(os.getenv("DOWNLOAD_DIR"),'EMP_TEMP_SEX_*.csv.gz')

dest_dir = os.path.abspath(data_dir)
for gz_file in glob.glob(source):
    logger.info(gz_file)
    raw_data_file = os.path.join(data_dir, os.path.basename(gz_file)[:-3])
    with gzip.open(gz_file, 'rb') as f_in:
        with open(raw_data_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    data_dict['raw_data_file'].append(raw_data_file)

'''
Process the data 

Each dataset contains data categorized by both ISIC Revisions 3 (>2007) and 4 (>2007)
https://archive.unescwa.org/sites/www.unescwa.org/files/events/files/event_detail_id_681_tablesbtwnisicrev.pdf

Level 1:
- Rev 3 
    - Natural Sector: ECO_ISIC3_A - Economic activity (ISIC-Rev.3.1): A. Agriculture, hunting and forestry
        "01","Agriculture, hunting and related service activities"
        "011","Growing of crops; market gardening; horticulture"
        "0111","Growing of cereals and other crops n.e.c."
        "0112","Growing of vegetables, horticultural specialties and nursery products"
        "0113","Growing of fruit, nuts, beverage and spice crops"
        "012","Farming of animals"
        "0121","Farming of cattle, sheep, goats, horses, asses, mules and hinnies; dairy farming"
        "0122","Other animal farming; production of animal products n.e.c."
        "013","Growing of crops combined with farming of animals (mixed farming)"
        "0130","Growing of crops combined with farming of animals (mixed farming)"
        "014","Agricultural and animal husbandry service activities, except veterinary activities"
        "0140","Agricultural and animal husbandry service activities, except veterinary activities"
        "015","Hunting, trapping and game propagation including related service activities"
        "0150","Hunting, trapping and game propagation including related service activities"
        "02","Forestry, logging and related service activities"
        "020","Forestry, logging and related service activities"
        "0200","Forestry, logging and related service activities"
    - Natural Sector: ECO_ISIC3_B - Economic activity (ISIC-Rev.3.1): B. Fishing
        "B","Fishing"
        "05","Fishing, aquaculture and service activities incidental to fishing"
        "050","Fishing, aquaculture and service activities incidental to fishing"
        "0501","Fishing"
        "0502","Aquaculture"
- Rev 4
    - Natural Sector Total: ECO_ISIC4_A - Economic activity (ISIC-Rev.4): A. Agriculture; forestry and fishing
        "01","Crop and animal production, hunting and related service activities"
        "011","Growing of non-perennial crops"
        "0111","Growing of cereals (except rice), leguminous crops and oil seeds"
        "0112","Growing of rice"
        "0113","Growing of vegetables and melons, roots and tubers"
        "0114","Growing of sugar cane"
        "0115","Growing of tobacco"
        "0116","Growing of fibre crops"
        "0119","Growing of other non-perennial crops"
        "012","Growing of perennial crops"
        "0121","Growing of grapes"
        "0122","Growing of tropical and subtropical fruits"
        "0123","Growing of citrus fruits"
        "0124","Growing of pome fruits and stone fruits"
        "0125","Growing of other tree and bush fruits and nuts"
        "0126","Growing of oleaginous fruits"
        "0127","Growing of beverage crops"
        "0128","Growing of spices, aromatic, drug and pharmaceutical crops"
        "0129","Growing of other perennial crops"
        "013","Plant propagation"
        "0130","Plant propagation"
        "014","Animal production"
        "0141","Raising of cattle and buffaloes"
        "0142","Raising of horses and other equines"
        "0143","Raising of camels and camelids"
        "0144","Raising of sheep and goats"
        "0145","Raising of swine/pigs"
        "0146","Raising of poultry"
        "0149","Raising of other animals"
        "015","Mixed farming"
        "0150","Mixed farming"
        "016","Support activities to agriculture and post-harvest crop activities"
        "0161","Support activities for crop production"
        "0162","Support activities for animal production"
        "0163","Post-harvest crop activities"
        "0164","Seed processing for propagation"
        "017","Hunting, trapping and related service activities"
        "0170","Hunting, trapping and related service activities"
        "02","Forestry and logging"
        "021","Silviculture and other forestry activities"
        "0210","Silviculture and other forestry activities"
        "022","Logging"
        "0220","Logging"
        "023","Gathering of non-wood forest products"
        "0230","Gathering of non-wood forest products"
        "024","Support services to forestry"
        "0240","Support services to forestry"
        "03","Fishing and aquaculture"
        "031","Fishing"
        "0311","Marine fishing"
        "0312","Freshwater fishing"
        "032","Aquaculture"
        "0321","Marine aquaculture"
        "0322","Freshwater aquaculture"

Level 2:
- ISIC Rev 3
    - Fishing: EC2_ISIC3_B05 - Economic activity (ISIC-Rev.3.1), 2 digit level: 05 - Fishing, aquaculture and service activities incidental to fishing
- ISIC Rev 4
    - Fishing: EC2_ISIC4_A03 - Economic activity (ISIC-Rev.4), 2 digit level: 03 - Fishing and aquaculture

'''


def classify_rev(row):
    if row['classif1'][9] == 3:
      return '3'
    elif row['classif1'][9] == 4:
      return '4'

for file in data_dict['raw_data_file']:
    
    # read in the data as a pandas dataframe 
    df = pd.read_csv(file,encoding='latin-1') 
  
    # rename the time and area columns
    df.rename(columns={'time':'year'}, inplace=True)
    df.rename(columns={'ref_area':'area'}, inplace=True)
    
    column_list= ['source', 'indicator', 'level', 'type','classif1', 'obs_value', 'obs_status', 'note_indicator', 'note_source','note_classif']

    print(file[18:21])
    if file[18:21] == 'ECO':
        # Group natural sector totals for Rev 3
        code_list = ['ECO_ISIC3_A','ECO_ISIC3_B']
        df_3 = df[df['classif1'].isin(code_list)]
        df_3 = df_3.groupby(['area','year','sex']).agg({'indicator':'first','source':'first', 'obs_value':'sum', 'obs_status': 'first', 'note_indicator': 'first', 'note_source': 'first'}).reset_index()
        df_3['classif1'] = 'ECO_ISIC3_A, ECO_ISIC3_B'
        
        
        # append rev 4 data
        df_4 = df[df['classif1'] == 'ECO_ISIC4_A']
        df= pd.concat([df_3, df_4])
        df['level'] = '1'
        df['type'] = 'Natural Sector Total'
        df['rev'] = df.classif1.str[8]
        for column in column_list:
            df.rename(columns={column: column+'_natural'}, inplace=True)

        # store the processed df
        data_dict['processed_dfs'].append(df)

    elif file[18:21] == 'EC2':
        code_list = ['EC2_ISIC3_B05','EC2_ISIC4_A03']
        df = df[df['classif1'].isin(code_list)]
        df['level'] = '2'
        df['type'] = 'Fishing'
        df['rev'] = df.classif1.str[8]

        for column in column_list:
            df.rename(columns={column: column+'_fish'}, inplace=True)
        
        # store the processed df 
        data_dict['processed_dfs'].append(df)

df= pd.merge(data_dict['processed_dfs'][0], data_dict['processed_dfs'][1], how= 'outer', on=['area','year','sex','rev'])


# convert Year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')


# sort the new data frame by country and year
df= df.sort_values(by=['area','year','sex'])

# reorder the columns
df = df[['area', 'year', 'sex', 'indicator_fish', 'classif1_fish', 'source_fish',
       'obs_value_fish', 'obs_status_fish', 'note_indicator_fish',
       'note_source_fish','indicator_natural', 'classif1_natural', 'source_natural',
       'obs_value_natural', 'obs_status_natural', 'note_classif_natural',
       'note_indicator_natural', 'note_source_natural', 'datetime']]

complete_data= df[~df['indicator_fish'].isnull()]
countries= complete_data.area.unique()
print(countries)
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
