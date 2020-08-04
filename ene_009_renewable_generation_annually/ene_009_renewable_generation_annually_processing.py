"""Script to transform and upload IRENA's capacity data to Resource Watch.

IRENA information is available through a Tableau applet.
This data must be downloaded manually, it is not possible to acquire
through an HTTP GET as we can tell.

Once downloaded, only minor transformation is needed to prepare it for upload.
The core issue is that the information does not fall into a data cube without
aggregating some rows to fit with expectations around data dimensionality.

It seems the data should be keyed on the dimensions:
    - country
    - year
    - most granular technology (e.g. "offshore wind" not "wind")
    - on-grid/off-grid

When keyed in this way there are still many compound keys
that have multiple rows and need to be summed to produce the
values expressed in Tableau visualization.

"""

import os
import pandas as pd
from zipfile import ZipFile
import shutil
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
dataset_name = 'ene_009_renewable_generation_annually'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# data can be downloaded by following the steps in the 'Data Acquisition' section of the README file
# generate path to downloaded data file
download = os.path.join(os.path.expanduser("~"), 'Downloads', 'Export_Full_Data_data.csv')

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process data
'''

# read in csv file as Dataframe
df = pd.read_csv(raw_data_file, dtype=str)

# filter pumped storage plants just like IRENA default
df = df[df['Sub-technology'] != 'Pumped Storage']

# convert values from string to float because summing later
df['Values_asfloat'] = df['Values'].astype(float)

# subset into generation
generation_data = df[df['DataType'] == 'Electricity Generation']

# assuming GWh everywhere, check that; yes the field name has a space at the end
assert (generation_data['Unit '] == 'GWh').all()

# group by the key dimensions
grouped =  generation_data.groupby(['ISO', 'Years', 'Sub-technology', 'Type'])
# ensure Technology is mapped 1:1 with Sub-technology
assert grouped.agg({'Technology': lambda x: len(set(x)) == 1}).Technology.all()

# create the data frame, renaming values and organizing the column order
data = grouped.agg({
        'Values_asfloat': 'sum',  # sum the numeric capacity value
        'IRENA Label': 'first',  # take a long name for the country
        'Technology': 'first',  # take the technology (superclass) 
    }).reset_index().rename(columns={
        'ISO': 'iso_a3',
        'Years': 'year',
        'Sub-technology': 'subtechnology',
        'Technology': 'technology',
        'Type': 'grid_connection',
        'IRENA Label': 'country_name',
        'Values_asfloat': 'generation_GWh',
    })[[  # set a new column order
        'iso_a3',  # key
        'country_name',  # 1:1 with iso_a3
        'year', # key
        'subtechnology',  # key
        'technology',  # 1:n with subtechnology
        'grid_connection',  # key
        'generation_GWh'  # the numeric generation value in gigawatt-hours
    ]]


#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
data.to_csv(processed_data_file, index=False)

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