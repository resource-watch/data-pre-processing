import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from botocore.exceptions import NoCredentialsError
from zipfile import ZipFile
import datetime
import shutil
# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'cit_022_road_traffic_death_rates' #check
# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cit_022_road_traffic_death_rates'
path = os.path.join(os.getenv('PROCESSING_DIR'), dataset_name)
#move to this directory
os.chdir(path)
# create a new sub-directory within your specified dir called 'data'
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
'''
Download data and save to your data directory
Country-level data for Road traffic deaths can be downloaded at the following link:
https://apps.who.int/gho/data/node.main.A997?lang=en
Above the data table, you will see a 'CSV table' button on the right side of 'Download filtered data as:' text.
Once you click this button, a prompt will appear to download a file titled 'data.csv' to your Downloads folder.
'''
# insert the url used to download the data from the source website
url = 'https://apps.who.int/gho/athena/data/GHO/RS_196,RS_198?filter=COUNTRY:*&x-sideaxis=COUNTRY&x-topaxis=GHO;YEAR&profile=crosstable&format=csv'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'data.csv')
urllib.request.urlretrieve(url, raw_data_file)
'''
Process data
'''
# read in csv file as Dataframe
df=pd.read_csv(raw_data_file, header=1) # selecting 2nd row as the column names
#rename all the columns
df.rename(columns={df.columns[0]:'country'}, inplace=True)
df.rename(columns={df.columns[1]:'estimated_number_of_road_traffic_deaths_data'}, inplace=True)
df.rename(columns={df.columns[2]:'death_rate_per_100000'}, inplace=True)
# get the Estimated number of road traffic deaths by splitting
# 'estimated_number_of_road_traffic_deaths_data' column on '[' and getting the first
# element from the split. Store the second element from split to a new column 'bounds'
df[['estimated_number_of_road_traffic_deaths_data','bounds']]=df['estimated_number_of_road_traffic_deaths_data'].str.split('[', expand=True)
# create a new column for lower bound of estimated number of road traffic deaths
# split the values from column 'bounds' on '-' and insert the first element
# to the column 'estimated_lower_bound'
# replace values in the column 'bounds' with second element from this split
df[['estimated_lower_bound','bounds']]=df['bounds'].str.split('-', expand=True)
# rename 'bounds' column to 'estimated_upper_bound'
df.rename(columns={'bounds': 'estimated_upper_bound'}, inplace=True)
# remove unnecessary character ']' from the end of each row in 'estimated_upper_bound' column
df['estimated_upper_bound'] = df['estimated_upper_bound'].str[:-1]
# add a column for datetime with January 1, 2016 for every row
df['datetime'] = datetime.datetime(2016, 1, 1)
# rearrange the column names
df = df[['country', 'datetime', 'death_rate_per_100000','estimated_lower_bound',
         'estimated_number_of_road_traffic_deaths_data','estimated_upper_bound']]
# there are some rows which has empty spaces in between numbers in the
# 'estimated_number_of_road_traffic_deaths_data' column. remove those empty spaces
df['estimated_number_of_road_traffic_deaths_data'] = df['estimated_number_of_road_traffic_deaths_data'].str.replace(' ', '')
#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)
'''
Upload processed data to Carto
'''
print('Uploading processed data to Carto.')
#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(processed_data_file)
print('Carto table created: {}'.format(os.path.basename(processed_data_file).split('.')[0]))
#set dataset privacy to 'Public with link'
dataset.privacy = 'LINK'
dataset.save()
print('Privacy set to public with link.')
'''
Upload original data and processed data to Amazon S3 storage
'''
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        print("http://{}.s3.amazonaws.com/{}".format(bucket, s3_file))
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
print('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(raw_data_dir))
print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(processed_data_dir))
