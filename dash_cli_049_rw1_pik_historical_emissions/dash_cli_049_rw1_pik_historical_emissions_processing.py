import shutil
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
import logging
import glob
import datetime

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
dataset_name = 'dash_cli_049_rw1_pik_historical_emissions' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.climatewatchdata.org/data-explorer/historical-emissions?historical-emissions-data-sources=cait&historical-emissions-gases=all-ghg&historical-emissions-regions=All%20Selected&historical-emissions-sectors=total-including-lucf&page=1#data
From the dropdown menus above the table, select the following options:
    Data sources: PIK
    Countries and regions: World
    Sectors: All selected
    Gases: CO2, CH4, N2O, F-Gas
    Start year: 1850
    End year: 2017
Below the table, there is a 'Download Historical Emissions data' button. Click on the button and a zipped folder containing the data will be downloaded to your Downloads folder.
'''
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'historical_emissions.zip'))[0]

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# the path to the unprocessed data
raw_data_file = glob.glob(os.path.join(raw_data_file_unzipped, 'historical_emissions.csv'))[0]

# read in the data as a pandas dataframe
df = pd.read_csv(raw_data_file)

# since we are calculating the total GHG emissions of the world,
# we filter the dataframe to obtain the global GHG emission data
df = df[df.Country == 'World']

# convert the format of the dataframe from wide to long
df = pd.melt(df, id_vars=df.columns[:5])

# rename the 'variable', 'value', and 'Data source' columns to be 'datetime', 'yr_data', and 'source'
df.rename(columns={'variable':'datetime', 'value': 'yr_data', 'Data source': 'source'}, inplace=True)

# convert the year values in the 'datetime' column to be datetime objects
df['datetime'] = [datetime.datetime(int(x), 1, 1) for x in df.datetime]

# drop the unit column
df.drop('Unit', axis = 1, inplace = True)

# sum all types of greenhouse gas emissions for each sector every year
df = df.groupby(['Country', 'source', 'Sector', 'datetime']).sum().reset_index()

# add a column 'gas' to indicate the type of greenhouse gas emissions included in the dataset
df['gas'] = 'All GHG'

# add a column 'gwp' to indicate the type of global warming potential standard used in the calculation of greenhouse gas emissions
df['gwp'] = 'AR4'

# reorder the columns in the dataframe
df = df[['Country', 'source', 'Sector', 'gas', 'gwp', 'datetime', 'yr_data']]

# convert the column names to be in lowercase letters
df.columns = [x.lower() for x in df.columns]

#save processed dataset to csv
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
