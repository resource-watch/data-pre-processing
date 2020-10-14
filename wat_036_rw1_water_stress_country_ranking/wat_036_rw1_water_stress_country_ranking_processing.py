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
import shutil
import logging
import glob
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
# this should be a table name that is not currently in use
dataset_name = 'wat_036_rw1_water_stress_country_ranking' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.wri.org/applications/aqueduct/country-rankings/
Above the table, there is a 'Download ranking' button 
Click on it and the data will downloaded as an excel file to your Downloads folder
'''
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'Aqueduct30_Rankings_V01.xlsx'))[0]

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

# read in data stored in the 'results country' spreadsheet within the excel file to pandas dataframe
df = pd.read_excel(raw_data_file, 'results country')

'''
Process data
'''
# subset the dataframe based on the 'indicator_name' column to select baseline water stress indicator
df = df[df.indicator_name == 'bws']

# replace the '-9999' with nans 
df.replace({-9999: np.nan}, inplace = True)

# rename the column 'primary' to 'primary_country' since 'primary' is a reserved word in PostgreSQL
df.rename(columns = {'primary': 'primary_country'}, inplace = True)

# convert the dataframe from long to wide format 
# so the score, risk category, and country ranking calculated using different weights will be stored in separate columns 
df = df.pivot_table(index = ['iso_a3','iso_n3','primary_country','name_0','indicator_name', 'un_region', 'wb_region', 'population_2019_million'],
               columns = 'weight',
               values = ['score', 'score_ranked', 'cat', 'label'],
               aggfunc=lambda x: x).reset_index()

# rename the columns created in the previous step to indicate the weight used in the calculation of each column  
df.columns = [(weight + '_' + var).lower() if weight else var for (var, weight)in list(df)]

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
