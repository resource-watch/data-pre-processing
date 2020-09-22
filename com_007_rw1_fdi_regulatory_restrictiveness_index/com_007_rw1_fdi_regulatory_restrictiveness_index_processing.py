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
# this should be a table name that is not currently in use
dataset_name = 'com_007_rw1_fdi_regulatory_restrictiveness_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
http://stats.oecd.org/Index.aspx?datasetcode=FDIINDEX#
Above the table, there is a 'export' button that will lead to a dropdown menu containing different export options.
Once you select 'Text file (CSV)' from the menu, a new window will occur and allow you to download the data as a csv file to your Downloads folder.
'''
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'FDIINDEX_*.csv'))[0]

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

# read in data to pandas dataframe
df = pd.read_csv(raw_data_file)

'''
Process data
'''
# remove 'TIME' column because it is identical to the 'year' column
df = df.drop(columns = 'TIME')

# remove the column 'SECTOR' since it contains the same information as the column 'Sector/Industry'
# (SECTOR is a numeric column, while Sector/Industry' is text, so we will keep the more informative column)
df = df.drop(columns = 'SECTOR')

# remove columns with no values
df.dropna(axis=1)

# remove columns with only one unique value
for col in df.columns:
    if len(df[col].unique()) == 1:
        df.drop(col,inplace=True,axis=1)

# reformat the dataframe so each sector becomes a new column
pivoted = pd.pivot_table(df, index = ['LOCATION', 'Country','Year'], columns = 'Sector / Industry', values = 'Value').reset_index()

# rename columns, replacing or removing symbols and spaces, and
# making them all lowercase so that it matches Carto column name requirements
pivoted.columns = [re.sub('[().]', '', col.lower().replace('&', 'and').replace(' ', '_')) for col in pivoted.columns]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
pivoted.to_csv(processed_data_file, index=False)

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
