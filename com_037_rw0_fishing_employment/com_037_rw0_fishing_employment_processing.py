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
Download data, unzip, and save to your data directory

The data was downloaded manually from https://ilostat.ilo.org/data/# 
Scroll to the bottom of the page and click the ".gz" button for 
- ISIC Level 1: "Employment by sex and economic activity (thousands) | Annual" [Code: EMP_TEMP_SEX_ECO_NB_A] and
- ISIC Level 2: "Employment by sex and economic activity - ISIC level 2 (thousands) | Annual" [Code: EMP_TEMP_SEX_EC2_NB_A]
'''

# Create a data dictionary to store the relevant information about each file 
    # raw_data_file: empty list for raw data files (list)
    # processed_dfs: empty list for processed dataframes (list)

data_dict= {
    'raw_data_file': [],
    'processed_dfs': []
  } 

# Unzip the data and move the data from 'Downloads' into the data directory

# Grab each file with the corresponding names from the Downloads folder
source = os.path.join(os.getenv("DOWNLOAD_DIR"),'EMP_TEMP_SEX_*.csv.gz')
for gz_file in glob.glob(source):
    logger.info(gz_file)
    
    # create a path to the unzipped, raw data file 
    raw_data_file = os.path.join(data_dir, os.path.basename(gz_file)[:-3])
    
    # unzip the .gz file
    with gzip.open(gz_file, 'rb') as f_in:
        # open the raw data file
        with open(raw_data_file, 'wb') as f_out:
            # move the file from downloads to the data directory
            shutil.copyfileobj(f_in, f_out)

    # add the file to the data dictionary        
    data_dict['raw_data_file'].append(raw_data_file)

'''
Process the data 

Each dataset (ISIC Level 1 and Level 2) contains both ISIC Revisions 3.1 (before 2007) and 4 (after 2007) categotizations (more info here: 
https://archive.unescwa.org/sites/www.unescwa.org/files/events/files/event_detail_id_681_tablesbtwnisicrev.pdf). These two classifications systems 
require different processing depending on the level of the data.

At classfiication Level 1, in the 3rd revolution of the classifciation system (Rev 3.1) the Natural Sector Economic Activity was split into two classifications:
'A. Agriculture, hunting and forestry' [ECO_ISIC3_A] & 'B. Fishing' [ECO_ISIC3_B]. These will need to be combined. In the 4th revolition of the classifcation system 
(Rev 4) the Natural Sector Economic Activity is aggregated into one classification: A. Agriculture; forestry and fishing [ECO_ISIC4_A]

At classification Level 2, in Rev 3.1 Fishing Economic Activity is classified as '05 - Fishing, aquaculture and service activities incidental to fishing' 
[EC2_ISIC3_B05]. In Rev 4 Fishing Economic Activity is classified as '03 - Fishing and aquaculture' [EC2_ISIC4_A03].

'''

# Process each classification level
for file in data_dict['raw_data_file']:
    
    # read in the data as a pandas dataframe 
    df = pd.read_csv(file,encoding='latin-1') 
  
    # rename the time and area columns
    df.rename(columns={'time':'year'}, inplace=True)
    df.rename(columns={'ref_area':'area'}, inplace=True)
    
    # create a list of columns that will be duplicated when the tables are merged
    column_list= ['source', 'indicator', 'level', 'type','classif1', 'obs_value', 'obs_status', 'note_indicator', 'note_source','note_classif']

    # process the level 1 table
    if file[18:21] == 'ECO':
        # Group natural sector totals for Rev 3 rows and sum the observed values to get total employment in the natural sector
        # Filter the data to Rev 3 rows
        code_list = ['ECO_ISIC3_A','ECO_ISIC3_B']
        df_3 = df[df['classif1'].isin(code_list)]
        # Sum the observed values for a given area, year, and sex 
        df_3 = df_3.groupby(['area','year','sex']).agg({'indicator':'first','source':'first', 'obs_value':'sum', 'obs_status': 'first', 'note_indicator': 'first', 'note_source': 'first'}).reset_index()
        # Change the classification to reflect the aggregation
        df_3['classif1'] = 'ECO_ISIC3_A, ECO_ISIC3_B'
        
        # Append Rev 4 data (already an aggregated total)
        df_4 = df[df['classif1'] == 'ECO_ISIC4_A']
        df= pd.concat([df_3, df_4])

        # Add a column to reflect the level of the data (ISIC Level 1)
        df['level'] = '1'

        # Add a column to reflect the type of observed value (Natural Sector Total Employment)
        df['type'] = 'Natural Sector Total'

        # Add a column to reflect the classification system (Rev 3 or Rev 4)
        df['rev'] = df.classif1.str[8]

        # Add a suffix to columns that will be duplicated in the merge
        for column in column_list:
            df.rename(columns={column: column+'_natural'}, inplace=True)

        # store the processed df
        data_dict['processed_dfs'].append(df)

    # process the level 2 data
    elif file[18:21] == 'EC2':
        # Filter the data to data on fishing employment
        code_list = ['EC2_ISIC3_B05','EC2_ISIC4_A03']
        df = df[df['classif1'].isin(code_list)]
        
        # Add a column to reflect the level of the data (ISIC Level 2)
        df['level'] = '2'

        # Add a column to reflect the type of observed value (Fishing Employment)
        df['type'] = 'Fishing'

        # Add a column to reflect the classification system (Rev 3 or Rev 4)
        df['rev'] = df.classif1.str[8]

        # Add a suffix to columns that will be duplicated in the merge
        for column in column_list:
            df.rename(columns={column: column+'_fish'}, inplace=True)
        
        # store the processed data frames
        data_dict['processed_dfs'].append(df)

# Merge the processed data frames
df= pd.merge(data_dict['processed_dfs'][0], data_dict['processed_dfs'][1], how= 'outer', on=['area','year','sex','rev'])

# convert year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')

# sort the new data frame by country and year
df= df.sort_values(by=['area','year','sex'])

# reorder the columns
df = df[['area', 'year', 'sex', 'rev', 'indicator_fish', 'classif1_fish', 'source_fish',
       'obs_value_fish', 'obs_status_fish', 'note_indicator_fish',
       'note_source_fish','indicator_natural', 'classif1_natural', 'source_natural',
       'obs_value_natural', 'obs_status_natural', 'note_classif_natural',
       'note_indicator_natural', 'note_source_natural', 'datetime']]


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
