# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 14:22:50 2021

@author: Jason.Winik
"""

import pandas as pd
from pandas import DataFrame
import numpy as np
import io
import requests
import json
import os
import sys
import tabula
import dotenv
dotenv.load_dotenv('C:\\Users\\Jason.Winik\\OneDrive - World Resources Institute\\Documents\\GitHub\\cred\\.env')
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
gdal_path = os.getenv('GDAL_DIR')
if gdal_path not in sys.path:
    sys.path.append(gdal_path)
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
dataset_name = 'soc_026_gender_inequality_index' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Import table from Carto
'''
#https://carto.com/developers/sql-api/guides/copy-queries/
api_key = 'b246a1a3d6adcd53ef1e057c149a17ed8b7c3edb'
username = 'wri-rw'

q = 'SELECT * FROM soc_026_gender_gap_index_1'
url = 'https://wri-rw.carto.com/api/v2/sql'
r = requests.get(url, params={'api_key': api_key, 'q': q}).text
df_dict = json.loads(r)
df_carto = pd.DataFrame(df_dict['rows'])

'''
Process Data
'''
# Tabula .read_pdf() requirements
data = {'year':[2020, 2021],
        'link': ['http://www3.weforum.org/docs/WEF_GGGR_2020.pdf', 'http://www3.weforum.org/docs/WEF_GGGR_2021.pdf'],
        'page_GGGR': [9,10],
        'page_area_GGGR': [[59.9,59.9,713.215,548.026],[59.007,56.0,724.972,538.918]],
        'page_subindexes': [[12,13], [18,19]],
        'main index df': [],
        'subindex df':[]}
#df_pdf20 = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2020.pdf', pages='9',  stream=True)

    
#pull the tables
df_list = []
for i in range(len(data['year'])):
    df_list.append(tabula.read_pdf(data['link'][i], pages=data['page_GGGR'][i], area = [data['page_area_GGGR'][i]], stream=True))    
    df_list.append(tabula.read_pdf(data['link'][i], pages=data['page_subindexes'][i], stream=True))
        
#unpack the nested lists
df_all = [x for l in df_list for x in l]

#create a dictionary that splits up dataframes by year. (first three are 2020, next 2021)
years_list = {'year':[2020, 2021], 'dataframes': [df_all[0:3], df_all[3:]]}


#datacleaning by year
data_clean = []
for i in range(len(years_list['year'])):
    df_list_a = years_list['dataframes'][i][0].iloc[:, 0:3]
    df_list_b = years_list['dataframes'][i][0].iloc[:,5:8]
    df_list_b.columns = ['Rank', 'Country', 'Score']
    df_list_c = pd.concat([df_list_a, df_list_b]).reset_index(drop=True)
    data_clean.append(df_list_c)
    


