import urllib
import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from botocore.exceptions import NoCredentialsError
from zipfile import ZipFile

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'wat_064_cost_of_sustainable_water_management' #check

# set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/wat_064_cost_of_sustainable_water_management'
dir = os.getenv('PROCESSING_DIR')+dataset_name
#move to this directory
os.chdir(dir)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url='https://wriorg.s3.amazonaws.com/s3fs-public/achieving-abundance.zip'  #check

# download the data from the source
raw_data_file = data_dir+os.path.basename(url)
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
filename=raw_data_file_unzipped+'/Achieving_Abundance_Countries.xlsx'
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
processed_data_file = data_dir+dataset_name+'_edit.csv'
final_df.to_csv(processed_data_file, index=False)

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
