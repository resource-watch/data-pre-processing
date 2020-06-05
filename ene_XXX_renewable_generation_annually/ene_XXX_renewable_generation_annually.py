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
# set True to prevent uploading to S3 & Carto
# set False to do the upload - requires API keys in ENV
DRY_RUN = True

import os
import pandas as pd
from zipfile import ZipFile
import shutil

if not DRY_RUN:
    from carto.datasets import DatasetManager
    from carto.auth import APIKeyAuthClient
    import boto3
    from botocore.exceptions import NoCredentialsError


# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
CARTO_TABLE_NAME = 'ene_XXX_renewable_generation_annually'

# see this processing workflow README for info on the input file
LOCAL_INPUT_FILE = 'IRENA-full-data-table-2020.csv'
LOCAL_ZIPFILE_FOR_INPUT = '{0}.zip'.format(CARTO_TABLE_NAME)
LOCAL_OUTPUT_FILE = '{0}_edit.csv'.format(CARTO_TABLE_NAME)
LOCAL_ZIPFILE_FOR_OUTPUT = '{0}_edit.zip'.format(CARTO_TABLE_NAME)

# ensure required file is present
assert LOCAL_INPUT_FILE in os.listdir(os.curdir)


# read in csv file as Dataframe
df = pd.read_csv(LOCAL_INPUT_FILE, dtype=str)

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


# save processed dataset to csv
data.to_csv(LOCAL_OUTPUT_FILE, index=False)


if not DRY_RUN:
    # Upload processed data to Carto
    print('Uploading processed data to Carto.')
    #set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(
			api_key=os.getenv('CARTO_WRI_RW_KEY'),
			base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER'))
			)
    #set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)  # this is an unofficial API feature?
    #upload dataset to carto
    dataset = dataset_manager.create(LOCAL_OUTPUT_FILE)
    print('Carto table created: {}'.format(LOCAL_OUTPUT_FILE))
    #set dataset privacy to 'Public with link'
    dataset.privacy = 'LINK'
    dataset.save()
    print('Privacy set to public with link.')


# Copy the raw data into a zipped file to upload to S3
with ZipFile(LOCAL_ZIPFILE_FOR_INPUT, 'w') as z:
    z.write(LOCAL_OUTPUT_FILE, '{0}.csv'.format(CARTO_TABLE_NAME))

# Copy the processed data into a zipped file to upload to S3
with ZipFile(LOCAL_ZIPFILE_FOR_OUTPUT, 'w') as z:
    z.write(LOCAL_OUTPUT_FILE, LOCAL_OUTPUT_FILE)

if not DRY_RUN:
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

    # Upload raw data file to S3
    print('Uploading original data to S3.')
    uploaded_input = upload_to_aws(LOCAL_ZIPFILE_FOR_INPUT, 'wri-public-data',
            'resourcewatch/' + LOCAL_ZIPFILE_FOR_INPUT)

    print('Uploading processed data to S3.')
    # Upload processed data file to S3
    uploaded_output = upload_to_aws(LOCAL_ZIPFILE_FOR_OUTPUT, 'wri-public-data',
        'resourcewatch/' + LOCAL_ZIPFILE_FOR_OUTPUT)
