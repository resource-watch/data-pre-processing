import pandas as pd
from pandas import DataFrame
import numpy as np
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




'''
Import table from Carto
'''
#https://carto.com/developers/sql-api/guides/copy-queries/
api_key = 'b246a1a3d6adcd53ef1e057c149a17ed8b7c3edb'
username = 'wri-rw'

q = 'SELECT * FROM soc_026_gender_gap_index_1'
url = 'https://wri-rw.carto.com/api/v2/sql'
r = requests.get(url, params={'api_key': api_key, 'q': q}).text

col_soc_026 = ['cartodb_id', 'country', 'economic_participation_and_opportunity_subindex_rank', 'economic_participation_and_opportunity_subindex_score', 'educational_attainment_subindex_rank',
'educational_attainment_subindex_score', 'field_13', 'field_14', 'field_15', 'health_and_survival_subindex_rank', 'health_and_survival_subindex_score', 'overall_index_rank', 'overall_index_score', 'political_empowerment_subindex_rank', 'political_empowerment_subindex_score', 'the_geom', 'the_geom_webmercator', 'year']
df_dict = json.loads(r)


df_carto = pd.DataFrame(df_dict['rows'])
#pd.DataFrame.from_dict(list(df_dict.items()),orient = 'index', columns=col_soc_026)



'''
Process data
'''

#2021

# read in data to tabulas/ pandas dataframe
# https://pypi.org/project/tabula-py/
# https://nbviewer.jupyter.org/github/chezou/tabula-py/blob/master/examples/tabula_example.ipynb

r_url = requests.get(url)
df_pdf21 = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2021.pdf', pages=['10','18','19'], stream=True)

#remove first dataframe in list with titles
df = df_pdf21[1]

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
df_concat['overall_index_score'] = df_concat['Unnamed: 0'].str.split(' ').str[0]


#drop unused columns from last step
df_concat = df_concat.drop(['Unnamed: 0', 'Unnamed: 1', 'Rank.1'], axis=1)
df_concat.columns = ['overall_index_rank', 'country', 'overall_index_score']
df_concat['year'] = np.where(df_concat['overall_index_score'], 2021, 0)

#reorder columns to match dataset from pdf
df_concat = df_concat[['country', 'overall_index_rank','overall_index_score','year']]

#Four subindexes
df_pdf21_2 = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2021.pdf', pages=['10','18','19'], stream=True)

#remove first dataframe in list with titles
df = df_pdf[1]




