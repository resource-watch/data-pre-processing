import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from botocore.exceptions import NoCredentialsError
from zipfile import ZipFile
import shutil

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'ene_033_energy_consumption' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ene_033_energy_consumption'
path = os.getenv('PROCESSING_DIR')+dataset_name
#move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory

Country-level data for total energy consumption can be downloaded at the following link:
https://www.eia.gov/beta/international/data/browser/#/?pa=000000001&c=ruvvvvvfvtvnvv1urvvvvfvvvvvvfvvvou20evvvvvvvvvnvvuvs&ct=0&ug=4&vs=INTL.44-2-AFG-QBTU.A&cy=2017&vo=0&v=H&start=1980&end=2017

Below the map and above the data table, you will see a 'Download' button on the right side of the screen
Once you click this button, a dropdown menu will appear. Click on 'Table' under the 'Data (CSV)' section.
This will download a file titled 'International_data.csv' to your Downloads folder.
'''
download = os.path.expanduser("~")+'/Downloads/International_data.csv'

# Move this file into your data directory
raw_data_file = data_dir+os.path.basename(download)
shutil.move(download,raw_data_file)

'''
Process data
'''
# read in csv file as Dataframe
df = pd.read_csv(raw_data_file, header=[4])

#drop first column from table with no data in it
df = df.drop(df.columns[0], axis=1)

#drop first two rows from table with no data in it
df = df.drop([0,1,2], axis=0)
df=df.reset_index(drop=True)

#rename first two unnamed columns
df.rename(columns={df.columns[0]:'country'}, inplace=True)
df.rename(columns={df.columns[1]:'unit'}, inplace=True)

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
processed_data_file = data_dir+dataset_name+'_edit.csv'
df_long.to_csv(processed_data_file, index=False)


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
raw_data_dir = data_dir+dataset_name+'.zip'
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = data_dir+dataset_name+'_edit'+'.zip'
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(processed_data_dir))
