import pandas as pd
import io
import requests
import os
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from zipfile import ZipFile
from botocore.exceptions import NoCredentialsError
import shutil

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'com_007_FDI_regulatory_restrictiveness_Index' #check

# set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/com_007_FDI_regulatory_restrictiveness_Index'
dir = os.path.join(os.getenv('PROCESSING_DIR'), dataset_name)
#move to this directory
os.chdir(dir)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
http://stats.oecd.org/Index.aspx?datasetcode=FDIINDEX#
Above the table, there is a 'export' button that will lead to a dropdown menu containing different export options.
Once you select 'Text file (CSV)' from the menu, a new window will occur and allow you to download the data as a csv file to your Downloads folder.
'''
download = os.path.join(os.path.expanduser("~"), 'Downloads', 'FDIINDEX_23072020142137563.csv')

# Move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

# read in data to pandas dataframe
df = pd.read_csv(raw_data_file)

'''
Process data
'''
# remove duplicate column 
df = df.drop(columns = 'TIME')

# remove columns with no values 
df = df.drop(columns = ['Flag Codes', 'Flags'])

# remove columns with only one unique value 
df = df.drop(columns = ['Type of restriction', 'SERIES', 'Series', 'RESTYPE'])

# remove the column 'SECTOR' since it contains the same information as the column 'Sector/Industry'
df = df.drop(columns = 'SECTOR')

# reformat the dataframe so each sector becomes a new column 
pivoted = pd.pivot_table(df, index = ['LOCATION', 'Country','Year'], columns = 'Sector / Industry', values = 'Value').reset_index()

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
pivoted.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
print('Uploading processed data to Carto.')
#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
print (os.getenv('CARTO_WRI_RW_KEY'))
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
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'),
                      aws_secret_access_key=os.getenv('aws_secret_access_key'))
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
with ZipFile(raw_data_dir, 'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir, 'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(processed_data_dir))
