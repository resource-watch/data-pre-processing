import pandas as pd
from pandas import DataFrame
import io
import requests
import json
import os
import sys
import tabula
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import logging
from zipfile import ZipFile
from carto.datasets import DatasetManager


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
dataset_name = 'soc_026_gender_inequality_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'http://www3.weforum.org/docs/WEF_GGGR_2021.pdf' #check

# read in data to tabulas/ pandas dataframe
# https://pypi.org/project/tabula-py/
# https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb
r_url = requests.get(url)
df_pdf = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2021.pdf', pages='10', stream=True)

'''
Import table from Carto
'''
#https://carto.com/developers/sql-api/guides/copy-queries/
api_key = 'b246a1a3d6adcd53ef1e057c149a17ed8b7c3edb'
username = 'wri-rw'

q = 'SELECT * FROM soc_026_gender_gap_index_1'
url = 'https://wri-rw.carto.com/api/v2/sql'
r = requests.get(url, params={'api_key': api_key, 'q': q}).text
r.raise_for_status()




'''
Process data
'''
years = ['2006','2008','2009','2010','2011','2012', '2013', '2014','2015','2016', '2017', '2018', '2020', '2021']
page_number = [15, ]
links = ['http://www3.weforum.org/docs/WEF_GenderGap_Report_2006.pdf', ]



#2021

#remove first dataframe in list with titles
df = df_pdf[1]

#remove rows without a country
df = df.dropna(subset = ['Country'])
df = df.reset_index(drop=True)

#replace comma with decimal
df = df.replace(',','.', regex=True)
# df = df.replace('+','', regex=True) How do I replace the + and - ? Do I need to?

#Remove first and second halves of df, then concatenate
df_first_half = df[['Rank', 'Country', 'Unnamed: 0', 'Rank.1', 'Unnamed: 1']]
df_second_half = df[['Rank.2','Country.1', 'Unnamed: 2', 'Rank.3', 'Unnamed: 3']]
df_second_half.columns = ['Rank', 'Country', 'Unnamed: 0', 'Rank.1', 'Unnamed: 1']

#concatenate
frames = [df_first_half, df_second_half]
df_concat = pd.concat(frames).reset_index(drop=True) 

#remove space after Gender Gap Index score, and change in score from 2016 and 2020
df_concat['Score'] = df_concat['Unnamed: 0'].str.split(' ').str[0]
df_concat['Score change 2020'] = df_concat['Unnamed: 1'].str.split(' ').str[0]
df_concat['Score change 2016'] = df_concat['Unnamed: 1'].str.split(' ').str[1]

#drop unused columns from last step
df_concat = df_concat.drop(['Unnamed: 0', 'Unnamed: 1'], axis=1)
df_concat.columns = ['Rank', 'Country', 'Rank Change', 'Score', 'Score change 2020', 'Score change 2016']

#reorder columns to match dataset from pdf
df_concat = df_concat[['Rank', 'Country', 'Score', 'Rank Change', 'Score change 2020', 'Score change 2016']]


# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_excel(raw_data_file, header = False, index = False)


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
s3_prefix = 'resourcewatch'

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
