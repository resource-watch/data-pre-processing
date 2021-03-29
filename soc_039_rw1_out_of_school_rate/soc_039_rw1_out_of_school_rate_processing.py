import pandas as pd
import os
import urllib.request
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import logging
import datetime
import glob
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
# this should be a table name that is not currently in use
dataset_name = 'soc_039_rw1_out_of_school_rate'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Data can be downloaded at the following link:
http://data.uis.unesco.org/Index.aspx
From the left panel, click to select 'EDUCATION' - 'Sustainable Development Goals 1 and 4' - '4.1.4 Out-of-school rate'.
Above the table, there is a 'Export' button that will lead to a dropdown menu containing different export options.
Once you select 'Text file (CSV)' from the menu, a new window will occur and allow you to download the data as a csv file to your Downloads folder.
'''
# the path to the downloaded data file in the Downloads folder
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'SDG_*.csv'))[0]

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process data
'''
# read the data into a pandas dataframe
df = pd.read_csv(raw_data_file)

# extract subset to only retain 'Out-of-school rate for children, adolescents and youth of primary, lower secondary and upper secondary school age, both sexes (%)' in the 'Indicator' column
df = df.loc[df['Indicator'] == 'Out-of-school rate for children, adolescents and youth of primary, lower secondary and upper secondary school age, both sexes (%)']

# extract subset based on column 'LOCATION', to only retain country-level data
df = df[df.LOCATION.apply(lambda x: len(str(x))<5)]

# remove column 'TIME' since it contains the same information as the column 'Time'
# remove column 'Flag Codes' since it contains the same information as the column 'Flags'
df = df.drop(columns = ['TIME','Flag Codes'])

# replace NaN in the table with None
df = df.where((pd.notnull(df)), None)

# remove rows where the 'Value' column is None
df = df.dropna(subset=['Value'])

# remove data in 2020 since it only has data for one country
df = df.loc[df.Time!=2020]

# convert the years in the 'Time' column to datetime objects and store them in a new column 'datetime'
df['datetime'] = [datetime.datetime(x, 1, 1) for x in df.Time]

# convert the column names to lowercase to match the column name requirements of Carto 
df.columns = [x.lower() for x in df.columns]

# save dataset to csv
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
