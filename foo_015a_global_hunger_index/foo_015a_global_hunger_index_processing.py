import os
import pandas as pd
import urllib.request
import tabula
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from botocore.exceptions import NoCredentialsError
from zipfile import ZipFile

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'foo_015a_global_hunger_index' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/foo_015a_global_hunger_index'
path = os.getenv('PROCESSING_DIR')+dataset_name
#move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'https://www.globalhungerindex.org/pdf/en/2019.pdf' #check

# download the data from the source
raw_data_file = data_dir+os.path.basename(url)
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# read in data from Table 2.1 GLOBAL HUNGER INDEX SCORES BY 2019 GHI RANK, which is on page 17 of the report
df_raw=tabula.read_pdf(raw_data_file,pages=17) #check

#remove headers and poorly formatted column names (rows 0, 1)
df_raw=df_raw.iloc[2:]

#get first half of table (columns 1-5, do not include rank column)
df_a=df_raw.iloc[:, 1:6]
#name columns
col_names = ["Country", "2000", "2005", "2010", "2019"] #check
df_a.columns = col_names
#get second half of table (columns 7-11, do not include rank column) and drop empty rows at end
df_b=df_raw.iloc[:, 7:12].dropna(how='all')
#name columns
df_b.columns = col_names

#combine first and second half of table
df = pd.concat([df_a, df_b], ignore_index=True, sort=False)

# clean the dataframe
# replace <5 with 5
df= df.replace('<5', 5)
#replace — in table with None
df = df.replace({'—': None})

#convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
df_long = pd.melt (df, id_vars= ['Country'] , var_name = 'year', value_name = 'hunger_index_score')

#convert year column from object to integer
df_long.year=df_long.year.astype('int64')
#convert hunger_index_score column from object to number
df_long.hunger_index_score = df_long.hunger_index_score.astype('float64')
#replace NaN in table with None
df_long=df_long.where((pd.notnull(df_long)), None)

#add rows for countries with insuffient data, but significant concern, as noted here:
# https://www.globalhungerindex.org/results.html#box-2-1

#add a column to our dataframe to store this flag - it will be False for all the countries already in our table
df_long['sig_concern'] = False

#make a list of countries for which there is insuffient data, but significant concern
sig_concern = ['Burundi', 'Comoros', 'Democratic Republic of Congo', 'Eritrea', 'Libya', 'Papua New Guinea', 'Somalia',
               'South Sudan', 'Syrian Arab Republic']

#add a new row to the dataframe for each of these countries, there will be no index score, but we will mark the flag as True
for country in sig_concern:
    row = [country, 2019, None, True]
    df_long = df_long.append(pd.Series(row, index=df_long.columns), ignore_index=True)

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'_edit.csv'
df_long.to_csv(csv_loc, index=False)


'''
Upload processed data to Carto
'''
print('Uploading processed data to Carto.')
#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)
print('Carto table created: {}'.format(os.path.basename(csv_loc).split('.')[0]))
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
    zip.write(csv_loc, os.path.basename(csv_loc))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(processed_data_dir))
