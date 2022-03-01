import logging
import pandas as pd
import glob
import os
import sys
import dotenv
#insert the location of your .env file here:
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import zipfile
from zipfile import ZipFile
import shutil

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
# using preexisting table for this dataset
dataset_name = 'soc_043_rw0_refugees_internally_displaced_persons' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
https://www.unhcr.org/refugee-statistics/download

One csv file was downloaded from the explorer
after selecting the following options from menu:
    
    Dataset: Population figures
    Display type: Totals
    Population type: All options selected
    Years: 1951-2020
    Country of origin: All countries
    Country of destination: All countries
    
The second csv file was downloaded from the explorer
after selecting the following options from menu: 

    Dataset: Solutions
    Display type: Totals
    Solution type: All options selected
    Years: 1951-2020
    Country of origin/return: All countries
    
'''

# download the data from the source
logger.info('Downloading raw data')
# Create list to store both the csv file and zipped shapefile paths
downloads = []
downloads.append(glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'populations.zip'))[0])
downloads.append(glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'solutions.zip'))[0])

# move this file into your data directory
# Create file paths where the excel files will be stored
raw_data_file = [os.path.join(data_dir,os.path.basename(download)) for download in downloads]
for index, download in enumerate(downloads):
    shutil.move(download,raw_data_file[index])

# unzip population data
population_unzipped = raw_data_file[0].split('.')[0]
zip_ref = ZipFile(raw_data_file[0], 'r')
zip_ref.extractall(population_unzipped)
zip_ref.close()

# unzip solutions data
solutions_unzipped = raw_data_file[1].split('.')[0]
zip_ref = ZipFile(raw_data_file[1], 'r')
zip_ref.extractall(solutions_unzipped)
zip_ref.close()

'''
Process csv files
'''
# read populations csv data to pandas dataframe
filename1=os.path.join(population_unzipped, 'population.csv')
population = pd.read_csv(filename1, skiprows=14)

# read solutions csv data to pandas dataframe
filename2=os.path.join(solutions_unzipped, 'solutions.csv')
solutions = pd.read_csv(filename2, skiprows=15)

# merge both dataframes on "Country of origin","Country of asylum", and "year"
df_edit = population.merge(solutions, how='outer', on=['Year','Country of origin','Country of origin (ISO)','Country of asylum (ISO)','Country of asylum'])

# we create a dictionary to rename columns in the same way as the preexisting carto table
column_dict = {'Country of origin': 'origin',
               'Country of asylum': 'country_territory_of_asylum_residence',
                'Asylum-seekers': 'asylum_seekers_pending_cases',
               'Returned refugees':'returned_refugees',
               'IDPs of concern to UNHCR':'internally_displaced_persons_idps',
               'Returned refugees':'returned_refugees',
               'Returned IDPss':'returned_idps','Stateless persons':'stateless_persons',
               'Others of concern':'others_of_concern'
              }


df_edit.rename(columns=column_dict,inplace=True)
# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]
# replace spaces and special characters in column headers with '_" 
df_edit.columns = df_edit.columns.str.replace("'", '_')

# We create a new column to sum the refugee like situations into a single column
column_list = ['refugees under unhcr_s mandate','venezuelans displaced abroad','resettlement arrivals']
df_edit["refugees_incl_refugee_like_situations"] = df_edit[column_list].sum(axis=1)
# Drop columns that we won't use
df_edit.drop(['country of origin (iso)', 'country of asylum (iso)', 
              'refugees under unhcr_s mandate', 'venezuelans displaced abroad',
              'resettlement arrivals','naturalisation'], axis=1, inplace=True)
# We create a new column to sum total
column_list2 = ['refugees_incl_refugee_like_situations','asylum_seekers_pending_cases','returned_refugees',
               'internally_displaced_persons_idps','returned_idps','stateless_persons','others_of_concern']
df_edit['total_population'] = df_edit[column_list2].sum(axis=1)
# convert the data type of the column 'total_population' to integer
df_edit['total_population'] = df_edit['total_population'].astype('int64')
# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)
# rearrange column names
column_names = ['year','country_territory_of_asylum_residence','origin','refugees_incl_refugee_like_situations',
                'asylum_seekers_pending_cases','returned_refugees','internally_displaced_persons_idps',
                'returned_idps','stateless_persons','others_of_concern','total_population']
df_edit = df_edit.reindex(columns=column_names)
# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_edit.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK', collision_strategy = 'overwrite')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))
logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file)) 
        
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
