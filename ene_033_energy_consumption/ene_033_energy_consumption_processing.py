import os
import pandas as pd
import sys
import glob
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
dataset_name = 'ene_033_energy_consumption' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Country-level data for total energy consumption can be downloaded at the following link:
https://www.eia.gov/international/data/world/total-energy/total-energy-consumption?pd=44&p=0000000010000000000000000000000000000000000000000000000000u&u=0&f=A&v=mapbubble&a=-&i=none&vo=value&&t=C&g=00000000000000000000000000000000000000000000000001&l=249-ruvvvvvfvtvnvv1vrvvvvfvvvvvvfvvvou20evvvvvvvvvvvvvvs&s=315532800000&e=1483228800000

Below the map and above the data table, you will see a 'Download' button on the right side of the screen
Once you click this button, a dropdown menu will appear. Click on 'Table' under the 'Data (CSV)' section.
This will download a file titled 'International_data.csv' to your Downloads folder.
'''
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'INT-Export*.csv'))[0]

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

'''
Process data
'''
# read in csv file as Dataframe
df = pd.read_csv(raw_data_file, header=[1])

#drop first column from table with no data in it
df = df.drop(df.columns[0], axis=1)

#drop first two rows from table since we are interestedin energy consumption of each country
df = df.drop([0,1], axis=0)
df=df.reset_index(drop=True)

#rename first two unnamed columns
df.rename(columns={df.columns[0]:'country'}, inplace=True)

#replace — in table with None
df = df.replace({'--': None})

#convert tables from wide form (each year is a column) to long form (a single column of years and a single column of values)
year_list = [str(year) for year in range(1980, 2018)] #check
df_long = pd.melt (df, id_vars= ['country'],
                   value_vars = year_list,
                   var_name = 'year',
                   value_name = 'energy_consumption_quadBTU')

#convert year and value column from object to integer
df_long.year=df_long.year.astype('int64')
df_long.energy_consumption_quadBTU=df_long.energy_consumption_quadBTU.astype('float64')

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