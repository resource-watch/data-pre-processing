import urllib
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
dataset_name = 'soc_091_global_peace_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'http://visionofhumanity.org/app/uploads/2020/02/GPI-2019-overall-scores-2008-2019.xlsx' #check

# download the data from source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# read in the 'Overall Scores' sheet of the Excel file as a dataframe
df=pd.read_excel(raw_data_file, sheet_name="Overall Scores", header=3) # selecting 4th row as the column names

# Remove all columns after column index 12 because they are empty
df.drop(df.iloc[:, 13:], inplace = True, axis = 1)

#convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
df_long = pd.melt (df, id_vars= ['Country'] , var_name = 'year', value_name = 'gpi_score')

#convert year column from object to integer
df_long.year=df_long.year.astype('int64')

#convert gpi_score column from object to number
df_long.gpi_score = df_long.gpi_score.astype('float64')

#replace NaN in table with None
df_long=df_long.where((pd.notnull(df_long)), None)

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_long.to_csv(processed_data_file, index=False)

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