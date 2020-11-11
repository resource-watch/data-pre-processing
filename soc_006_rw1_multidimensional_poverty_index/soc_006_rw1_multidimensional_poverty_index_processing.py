import io
import requests
import pandas as pd
import datetime
import re
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
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
dataset_name = 'soc_006_rw1_multidimensional_poverty_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://hdr.undp.org/sites/default/files/2020_mpi_statistical_data_table_1_and_2_en.xlsx'

# read in data to pandas dataframe
r = requests.get(url)
df = pd.read_excel(io.BytesIO(r.content), encoding='utf8', header=None, index = False)

# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_csv(raw_data_file, header = False, index = False)

'''
Process data
'''
# year of data 
year = 2019 # check 

# remove empty columns
df.dropna(axis = 1, how = 'all', inplace = True)

# remove rows with no data except in the first column
# these are the notes that we don't want to include in the Carto table 
df.dropna(axis = 0, how = 'all', subset = df.columns[1:], inplace = True)

# combine the strings in the first 4 rows of the dataframe to create headers
headers = []
for col in df.columns: 
    header = [x if pd.isnull(x) == False else ' ' for x in list(df[:4][col])]
    headers.append(''.join(header).strip())

# remove the first 4 rows since we have stored their information in the headers 
df = df[4:]

# assign headers to the columns 
df.columns = headers 

# drop columns that only contain footnotes 
df = df[[x for x in headers if len(x) > 1]].reset_index()

# extract the survey codes from the 'Multidimensional Poverty IndexYear and survey2008-2019' column
# and store them in a new column 'survey'
df['survey'] = [x[-1:] for x in df['Multidimensional Poverty IndexYear and survey{}-{}'.format(year-11, year)]]

# extract the year of surveys from the 'Multidimensional Poverty IndexYear and survey2008-2019' column
# and store them in a new column 'yr_survey'
df['yr_survey'] = [x[:-1].strip() 
                   for x in df['Multidimensional Poverty IndexYear and survey{}-{}'.format(year-11, year)]]

# drop the column 'index', 'Multidimensional Poverty IndexYear and survey2008-2019'
df.drop(columns = ['index', 'Multidimensional Poverty IndexYear and survey{}-{}'.format(year-11, year)], 
        inplace = True)

# rename columns to make column names more concise 
df.rename(columns = {'IndexValue': 'index_value',
                     'SDG 1.2Population in multidimensional povertyHeadcount(%)': 'population_multidimensional_poverty_headcount_percent',
                     'Contribution of deprivation in dimension to overall poverty(%)Health': 'health_contri_deprivation_percent',
                     'Education': 'education_contri_deprivation_percent', 
                     'Standard of living': 'standard_living_contri_deprivation_percent',
                     'Number of poor (year of the survey)(thousands)': 'number_poor_yr_survey_thousands',
                     'Number of poor ({})(thousands)'.format(year-1): 'number_poor_{}_thousands'.format(year-1),
                     'SDG 1.2Population living below income poverty line\n(%)National poverty line{}-{}'.format(year-11, year): 
                         'percent_pop_below_poverty_line_{}_{}'.format(year-11, year),
                     'SDG 1.1 PPP $1.90 a day{}-{}'.format(year-11, year-1): 'percent_pop_below_190_{}_{}'.format(year-11, year-1)},
          inplace = True)

# replace % with '_percent' and replace space and special characters within the column names with underscores
# also convert all the letters in column names to lower case 
df.columns = [re.sub(' *.%.','_percent', x).lower().strip().replace(' ', '_') for x in df.columns]

# remove data of regions 
df = df[df.survey != '—']

# replace '..' with None 
df.replace({'..': None}, inplace = True)

# except the column 'country', 'survey', and 'yr_survey'
# set the data type of the columns to float 
for col in df.columns: 
    if col not in ['country', 'survey', 'yr_survey']:
        df[col] = df[col].astype('float')

# create a new column 'release_dt' to store the year the data was released as its first date 
# the year will change every time we update this dataset 
df['release_dt'] = datetime.datetime(2020, 1, 1)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

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
