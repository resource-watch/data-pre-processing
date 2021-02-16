import logging
import pandas as pd
import glob
import os
import sys
import dotenv
#insert the location of your .env file here:
dotenv.load_dotenv('/home/eduardo/Documents/RW_github/cred/.env')
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import shutil
from zipfile import ZipFile
import cartoframes
CARTO_USER = os.environ.get('CARTO_USER')
CARTO_KEY = os.environ.get('CARTO_KEY')

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
dataset_name = 'soc_002_gender_development_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded from:
http://hdr.undp.org/sites/default/files/2020_statistical_annex_table_4.xlsx
'''

# download the data from the source
logger.info('Downloading raw data')
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', '2020_statistical_annex_table_4.xlsx'))[0]

# move this file into your data directory
raw_data_file = os.path.join(data_dir, os.path.basename(download))
shutil.move(download,raw_data_file)

#We retrieve the carto table with country names used by Resource Watch
auth=cartoframes.auth.Credentials(username=CARTO_USER, api_key=CARTO_KEY)
countries_wri = cartoframes.read_carto('wri_countries_a', credentials=auth)
countries_wri = countries_wri[['name','iso_a3']]
# read the data into a pandas dataframe, we skip empty headers and footers
df_edit = pd.read_excel(raw_data_file, header = 6, skipfooter = 58)
#We drop empty columns
df_edit.drop(df_edit.columns[[3,5,7,9,11,13,15,17,19,21,23,25]], axis=1, inplace=True)
#We name columns based on existing soc_002_gender_development_index carto table
df_edit.columns = ['hdi_rank', 'country','gdi_value', 'gdi_group','hdi_value__female', 'hdi_value__male',
       'life_expectancy_at_birth__female', 'life_expectancy_at_birth__male',
       'expected_years_of_schooling__female','expected_years_of_schooling__male',
       'mean_years_of_schooling__female', 'mean_years_of_schooling__male',       
       'estimated_gross_national_income_per_capita__female','estimated_gross_national_income_per_capita__male'  
       ]
#We drop rows without country information
df_edit = df_edit[~df_edit.country.str.contains("HUMAN DEVELOPMENT")]
df_edit = df_edit[~df_edit.country.str.contains("OTHER COUNTRIES OR TERRITORIES")]
#We create dictionary to match names of countries from source with the names of wri_countries_a carto table
countries_dict = {
    "Hong Kong, China (SAR)":"Hong Kong",
    "United States":"United States of America",
    "Korea (Republic of)":"South Korea",
    "Czechia":"Czech Republic",
    "Brunei Darussalam":"Brunei",
    "Russian Federation":"Russia",
    "Bahamas":"The Bahamas",
    "Serbia":"Republic of Serbia",
    "Iran (Islamic Republic of)":"Iran",
    "North Macedonia":"Macedonia",
    "Moldova (Republic of)":"Moldova",
    "Bolivia (Plurinational State of)":"Bolivia",
    "Venezuela (Bolivarian Republic of)":"Venezuela",
    "Palestine, State of":"Palestine",
    "Viet Nam":"Vietnam",
    "Cabo Verde":"Cape Verde",
    "Micronesia (Federated States of)":"Federated States of Micronesia",
    "Lao People's Democratic Republic":"Laos",
    "Eswatini (Kingdom of)":"Swaziland",
    "Congo":"Republic of Congo",
    "Syrian Arab Republic":"Syria",
    "Côte d'Ivoire":"Ivory Coast",
    "Tanzania (United Republic of)":"United Republic of Tanzania",
    "Congo (Democratic Republic of the)":"Democratic Republic of the Congo",
    "Guinea-Bissau":"Guinea Bissau",
    "Korea (Democratic People's Rep. of)":"North Korea"    
}
#Replace names from source with dictionary names
df_edit["country"].replace(countries_dict, inplace=True)
#Merge with the countries table
df_edit = pd.merge(countries_wri, df_edit, left_on =['name'], right_on =['country'], how='right')
#Renaming columns to match preexisting carto table and replacing special characters
df_edit.rename(columns={'iso_a3': 'rw_country_code', 'name': 'rw_country_name'}, inplace=True)
df_edit = df_edit.replace(to_replace ='..', value = None, regex = True)
# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)
#Reorder columns in dataframe to match existing carto table
df_edit = df_edit[['hdi_rank', 'country', 'gdi_value', 'gdi_group', 'hdi_value__female', 'hdi_value__male', 'life_expectancy_at_birth__female', 'life_expectancy_at_birth__male', 'expected_years_of_schooling__female', 'expected_years_of_schooling__male', 'mean_years_of_schooling__female', 'mean_years_of_schooling__male', 'estimated_gross_national_income_per_capita__female', 'estimated_gross_national_income_per_capita__male','rw_country_code','rw_country_name']]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'.csv')
df_edit.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK', collision_strategy='overwrite')

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
