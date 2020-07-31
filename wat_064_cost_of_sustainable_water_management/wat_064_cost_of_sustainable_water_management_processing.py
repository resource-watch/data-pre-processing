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
dataset_name = 'wat_064_cost_of_sustainable_water_management' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url='https://wriorg.s3.amazonaws.com/s3fs-public/achieving-abundance.zip'  #check

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

#unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# Read in Achieving_Abundance_Countries data to pandas dataframe
filename=os.path.join(raw_data_file_unzipped, 'Achieving_Abundance_Countries.xlsx')
Achieving_Abundance_df=pd.read_excel(filename, header=1) # selecting 2nd as row as the column names

# Remove columns containing contextual information that are not part of the core dataset
Achieving_Abundance_df.drop(Achieving_Abundance_df.iloc[:, 9:], inplace = True, axis = 1)

# Change column name for total cost to make it easily interpretable
Achieving_Abundance_df.rename(columns={'Total': 'Total Cost'}, inplace=True)

# Convert each aspect of sustainable water management to a percent of total estimated cost. 
i = 0
upper_bound = (Achieving_Abundance_df.shape[1])

for col in Achieving_Abundance_df.columns: 
    # Generate a name for the column that will hold the percentages.
    low_col = col.lower() # convert to lower case
    fin_col =low_col.replace (" ", "_") # put '_' in between for better readability
    percent_col = fin_col+'_percent'
    # If the column is not the 'total cost' column calculate the values for the percent column.
    i += 1
    if 2 < i < (upper_bound):
        print('Calculating percent of the total estimated cost for ' + str(col))
        # Create & populate new columns by converting each sustainable water management category to rounded percents
        Achieving_Abundance_df[percent_col] = round((Achieving_Abundance_df[col]/Achieving_Abundance_df['Total Cost'])*100)

#replace all NaN with None
final_df=Achieving_Abundance_df.where((pd.notnull(Achieving_Abundance_df)), None)

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
final_df.to_csv(processed_data_file, index=False)

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