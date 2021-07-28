# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 14:22:50 2021

@author: Jason.Winik 
"""

import pandas as pd
from pandas import DataFrame
import numpy as np
from functools import reduce
import requests
import json
import os
import glob
import tabula
import urllib.request
utils_path = os.path.join(os.getenv('PROCESSING_DIR'),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import logging
from zipfile import ZipFile

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
dataset_name = 'soc_026_gender_gap_index_combined' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

#download the latest pdf report

def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)    
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()
 
download_file('http://www3.weforum.org/docs/WEF_GGGR_2021.pdf', "global_gender_gap_2021")
download_file('http://www3.weforum.org/docs/WEF_GGGR_2020.pdf', "global_gender_gap_2020")

'''
Download data
'''
# Tabula .read_pdf() requirements
# If table does not pull correctly, use "area = " within tabula.
# https://tabula.technology/ is what I used to determine area of the table
data = {'year':[2020, 2021],
        'link': ['http://www3.weforum.org/docs/WEF_GGGR_2020.pdf', 'http://www3.weforum.org/docs/WEF_GGGR_2021.pdf'],
        'page_GGGR': [9,10],
        'page_area_GGGR': [[59.9,59.9,713.215,548.026],[59.007,56.0,724.972,538.918]],
        'page_subindexes': [[12,13], [18,19]]}

    
#pull the tables
df_main_index_dict = {}
df_subindex_dict = {}
for year in data['year']:
    i = data['year'].index(year)
    df_main_index_dict[year] = tabula.read_pdf(data['link'][i], pages=data['page_GGGR'][i], area = [data['page_area_GGGR'][i]], stream=True)    
    df_subindex_dict[year] = tabula.read_pdf(data['link'][i], pages=data['page_subindexes'][i], stream=True)


'''
Process Data
'''

# the source has inconsistently named some countries
# define a mapping to correct country names
name_mapping = {'Bosnia  Herzegovina':'Bosnia and Herzegovina',
                'Bosnia Herzegovina':'Bosnia and Herzegovina',
                'Congo Dem Rep': 'Congo, Dem. Rep.',
                'Gambia':'Gambia, The',
                'Iran': 'Iran, Islamic Rep.',
                'Korea':'Korea, Rep.',
                'Macedonia':'North Macedonia',
                'Swaziland':'Eswatini',
                'Timor-leste':'Timor-Leste',
                'Viet Nam':'Vietnam'
}

# define column names of source data and for final dataframe after processing
source_cols = ['Rank', 'Country', 'Score']
processed_cols = ['overall_index_rank', 'country', 'overall_index_score', 'year']

# process main index
data_main_index = pd.DataFrame(columns=processed_cols)
for year, df_list in df_main_index_dict.items():
    # data tables are split in half with first and second half side by side
    # first we need to concatenate the left and right sides
    df_a = df_list[0].iloc[:, 0:3] #first half
    df_a.columns = source_cols
    df_b = df_list[0].iloc[:,5:8] #second half
    df_b.columns = source_cols
    df_concat = pd.concat([df_a, df_b]).reset_index(drop=True) #concat
    df_concat['year'] = year #create a column for year
    df_concat = df_concat.dropna(subset = ['Country']) #drop NA
    # replace inconsistent country names
    for country in name_mapping.keys():
        df_concat['Country'] = np.where(df_concat['Country']==country, name_mapping[country], df_concat['Country'])
    # drop asterisks from new countries in country column
    df_concat[['Country']] = df_concat[['Country']].replace('\*','', regex=True)
    # replace , with . to properly format decimals in Score column
    df_concat[['Score']] = df_concat[['Score']].replace(',','.', regex=True)
    # drop duplicate entry of score
    df_concat['Score'] = df_concat['Score'].str.split(' ').str[0]
    # rename columns
    df_concat.columns = processed_cols
    # add clean data to overall dataframe for main index
    data_main_index = pd.concat([data_main_index, df_concat]).reset_index(drop=True)


def process_subindex(subindex, l_r, page):
    if l_r=='left':
        start_i = 0
    else:
        start_i = 6
    cols_sub = [f'{subindex}_subindex_rank', 'country', f'{subindex}_subindex_score']
    df_subindex = pd.DataFrame(columns=cols_sub)
    for year, df_list in df_subindex_dict.items():
        df_a = df_list[page].iloc[:, start_i:start_i+3] #first half
        df_a.columns = cols_sub
        df_b = df_list[page].iloc[:, start_i+3:start_i+6] #second half
        df_b.columns = cols_sub
        df_concat = pd.concat([df_a, df_b]).reset_index(drop=True) #concat
        df_concat['year'] = year #create a column for year
        # replace , with . to properly format decimals in Score column
        df_concat[[cols_sub[2]]] = df_concat[[cols_sub[2]]].replace(',','.', regex=True)
        df_concat = df_concat.dropna(subset = ['country']) #drop NA
        # the source data has mistakenly replaced , with . in some country names
        # if there is a . after the first word of a country name, replace it with a comma
        df_concat['country'] = df_concat['country'].apply(lambda x: x.replace(str(x).split(' ')[0], str(x).split(' ')[0].replace('.', ',')))
        # replace inconsistent country names
        for country in name_mapping.keys():
            df_concat['country'] = np.where(df_concat['country']==country, name_mapping[country], df_concat['country'])
        # drop asterisks from new countries in country column
        df_concat[['country']] = df_concat[['country']].replace('\*','', regex=True)
        df_subindex = pd.concat([df_subindex, df_concat]).reset_index(drop=True)
    return df_subindex


econ_df = process_subindex('economic_participation_and_opportunity', l_r='left', page=0)
edu_df = process_subindex('educational_attainment', l_r='right', page=0)
health_df = process_subindex('health_and_survival', l_r='left', page=1)
political_df = process_subindex('political_empowerment', l_r='right', page=1)

# define the list of dataframes to merge
merge_list = [econ_df, edu_df, health_df, political_df]
df_processed = data_main_index.copy()
for df in merge_list:
    df_processed = pd.merge(df_processed, df, on = ['year', 'country'], how = 'outer')
        
# read in existing dataframe so we can merge the new data with the old data
api_key = os.getenv('CARTO_WRI_RW_KEY')
username = os.getenv('CARTO_WRI_RW_USER')
q = 'SELECT * FROM soc_026_gender_gap_index_combined'
url = 'https://wri-rw.carto.com/api/v2/sql'
r = requests.get(url, params={'api_key': api_key, 'q': q}).text
df_dict = json.loads(r)
df_carto = pd.DataFrame(df_dict['rows'])

# Merge new years with old
frames_carto_upload = [df_carto, df_processed]
df_carto_upload = pd.concat(frames_carto_upload).reset_index(drop=True)

#drop cartodb_id so that it can be reassigned during upload
df_carto_upload = df_carto_upload.drop('cartodb_id', axis=1)

#save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_carto_upload.to_csv(processed_data_file, index=False)

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
raw_data_pdfs = ['global_gender_gap_2021.pdf', "global_gender_gap_2020.pdf"]

pdf_path_2021 = os.path.abspath("global_gender_gap_2021")
pdf_path_2020 = os.path.abspath("global_gender_gap_2020")

raw_data_file = [pdf_path_2020, pdf_path_2021]
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
#Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
