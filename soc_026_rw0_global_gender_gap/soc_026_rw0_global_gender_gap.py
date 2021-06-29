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
#add year
df_concat['year'] = np.where(df_concat['overall_index_score'], 2021, 0)

#reorder columns to match dataset from pdf
df_concat = df_concat[['country', 'overall_index_rank','overall_index_score','year']]

#Four subindexes
df_pdf21_2 = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2021.pdf', pages=['10','18','19'], stream=True)

#1. Economic Information and Opportunity 
df2 = df_pdf21[2]
df2 = df2.replace(',','.', regex=True)

df2_first_econ = df2[['Rank', 'Country', 'Score (0–1)']]
df2_second_econ = df2[['Rank.1', 'Country.1', 'Score (0–1).1']]
df2_second_econ.columns = ['Rank', 'Country', 'Score (0–1)']

#concatenate and rename columns
frames2 = [df2_first_econ, df2_second_econ]
df_concat2 = pd.concat(frames2).reset_index(drop=True) 
df_concat2.columns = ['economic_participation_and_opportunity_subindex_rank','country',
       'economic_participation_and_opportunity_subindex_score']
#add year
df_concat2['year'] = np.where(df_concat2['economic_participation_and_opportunity_subindex_score'], 2021, 0)


#2. Educational Attainment
df2_first_edu = df2[['Rank.2', 'Country.2', 'Score (0–1).2']]
df2_second_edu = df2[['Rank.3', 'Country.3', 'Score (0–1).3']]
df2_second_edu.columns = ['Rank.2', 'Country.2', 'Score (0–1).2']

#concatenate and rename columns
frames3 = [df2_first_edu, df2_second_edu]
df_concat3 = pd.concat(frames3).reset_index(drop=True) 
df_concat3.columns = ['educational_attainment_subindex_rank','country',
       'educational_attainment_subindex_score']

#add year
df_concat3['year'] = np.where(df_concat3['educational_attainment_subindex_score'], 2021, 0)


#3. Health and Survival
df3 = df_pdf21[3]
df3 = df3.replace(',','.', regex=True)

df3_first_health = df3[['Rank', 'Country', 'Score (0–1)']]
df3_second_health = df3[['Rank.1', 'Country.1', 'Score (0–1).1']]
df3_second_health.columns = ['Rank', 'Country', 'Score (0–1)']

#concatenate and rename columns
frames4 = [df3_first_health, df3_second_health]
df_concat4 = pd.concat(frames4).reset_index(drop=True) 
df_concat4.columns = ['health_and_survival_subindex_rank','country',
       'health_and_survival_subindex_score']
#add year
df_concat4['year'] = np.where(df_concat4['health_and_survival_subindex_score'], 2021, 0)


#4. Political Empowerment
df3_first_pol = df3[['Rank.2', 'Country.2', 'Score (0–1).2']]
df3_second_pol = df3[['Rank.3', 'Country.3', 'Score (0–1).3']]
df3_second_pol.columns = ['Rank.2', 'Country.2', 'Score (0–1).2']

#concatenate and rename columns
frames5 = [df3_first_pol, df3_second_pol]
df_concat5 = pd.concat(frames5).reset_index(drop=True) 
df_concat5.columns = ['political_empowerment_subindex_rank','country',
       'political_empowerment_subindex_score']
#add year
df_concat5['year'] = np.where(df_concat5['political_empowerment_subindex_score'], 2021, 0)


#Merge the 5 tables together
df21_final = df_concat.merge(df_concat2,how='outer', left_on=['year','country'], right_on = ['year','country'])
df21_final = df21_final.merge(df_concat3,how='outer', left_on=['year','country'], right_on = ['year','country'])
df21_final = df21_final.merge(df_concat4,how='outer', left_on=['year','country'], right_on = ['year','country'])
df21_final = df21_final.merge(df_concat5,how='outer', left_on=['year','country'], right_on = ['year','country'])


'''
2020
'''

# read in data to tabulas/ pandas dataframe
df_pdf20 = tabula.read_pdf('http://www3.weforum.org/docs/WEF_GGGR_2020.pdf', pages=['9','12','13'], stream=True)

#remove first dataframe in list with titles
df20 = df_pdf20[1]

#remove rows without a country
df20 = df20.dropna(subset = ['Country'])
df20 = df20.reset_index(drop=True)

#replace comma with decimal
df20 = df20.replace(',','.', regex=True)

#Remove first and second halves of df, then concatenate
df20_first_half = df20[['Rank', 'Country', 'Score (0–1)']]
df20_second_half = df20[['Rank.1', 'Country.1', 'Score (0–1).1']]
df20_second_half.columns = ['Rank', 'Country', 'Score (0–1)']

#concatenate
frames20 = [df20_first_half, df20_second_half]
df20_concat = pd.concat(frames20).reset_index(drop=True) 

#remove space after Gender Gap Index score, and change in score from 2016 and 2020


#drop unused columns from last step
df20_concat.columns = ['overall_index_rank', 'country', 'overall_index_score']
#add year
df20_concat['year'] = np.where(df20_concat['overall_index_score'], 2020, 0)

#reorder columns to match dataset from pdf20
df20_concat = df20_concat[['country', 'overall_index_rank','overall_index_score','year']]

#Four subindexes

#1. Economic Information and Opportunity 
df202 = df_pdf20[2]
df202 = df202.replace(',','.', regex=True)

df202_first_econ = df202[['Rank', 'Country', 'Score (0–1)']]
df202_second_econ = df202[['Rank.1', 'Country.1', 'Score (0–1).1']]
df202_second_econ.columns = ['Rank', 'Country', 'Score (0–1)']

#concatenate and rename columns
frames202 = [df202_first_econ, df202_second_econ]
df20_concat2 = pd.concat(frames202).reset_index(drop=True) 
df20_concat2.columns = ['economic_participation_and_opportunity_subindex_rank','country',
       'economic_participation_and_opportunity_subindex_score']
#add year
df20_concat2['year'] = np.where(df20_concat2['economic_participation_and_opportunity_subindex_score'], 2020, 0)


#2. Educational Attainment
df202_first_edu = df202[['Rank.2', 'Country.2', 'Score (0–1).2']]
df202_second_edu = df202[['Rank.3', 'Country.3', 'Score (0–1).3']]
df202_second_edu.columns = ['Rank.2', 'Country.2', 'Score (0–1).2']

#concatenate and rename columns
frames3 = [df202_first_edu, df202_second_edu]
df20_concat3 = pd.concat(frames3).reset_index(drop=True) 
df20_concat3.columns = ['educational_attainment_subindex_rank','country',
       'educational_attainment_subindex_score']

#add year
df20_concat3['year'] = np.where(df20_concat3['educational_attainment_subindex_score'], 2020, 0)


#3. Health and Survival
df203 = df_pdf20[3]
df203 = df3.replace(',','.', regex=True)

df203_first_health = df203[['Rank', 'Country', 'Score (0–1)']]
df203_second_health = df203[['Rank.1', 'Country.1', 'Score (0–1).1']]
df203_second_health.columns = ['Rank', 'Country', 'Score (0–1)']

#concatenate and rename columns
frames4 = [df203_first_health, df203_second_health]
df20_concat4 = pd.concat(frames4).reset_index(drop=True) 
df20_concat4.columns = ['health_and_survival_subindex_rank','country',
       'health_and_survival_subindex_score']
#add year
df20_concat4['year'] = np.where(df20_concat4['health_and_survival_subindex_score'], 2020, 0)


#4. Political Empowerment
df203_first_pol = df203[['Rank.2', 'Country.2', 'Score (0–1).2']]
df203_second_pol = df203[['Rank.3', 'Country.3', 'Score (0–1).3']]
df203_second_pol.columns = ['Rank.2', 'Country.2', 'Score (0–1).2']

#concatenate and rename columns
frames5 = [df203_first_pol, df203_second_pol]
df20_concat5 = pd.concat(frames5).reset_index(drop=True) 
df20_concat5.columns = ['political_empowerment_subindex_rank','country',
       'political_empowerment_subindex_score']
#add year
df20_concat5['year'] = np.where(df20_concat5['political_empowerment_subindex_score'], 2020, 0)


#Merge the 5 tables together
df2020_final = df20_concat.merge(df20_concat2, how='outer', left_on=['year','country'], right_on = ['year','country'])
df2020_final = df2020_final.merge(df20_concat3, left_on=['year','country'], right_on = ['year','country'],how='outer')
df2020_final = df2020_final.merge(df20_concat4, left_on=['year','country'], right_on = ['year','country'],how='outer')
df2020_final = df2020_final.merge(df20_concat5, left_on=['year','country'], right_on = ['year','country'],how='outer')

'''
Merge 2020 and 2021
'''
frames_20_21 = [df2020_final, df21_final]
df_new_years = pd.concat(frames_20_21).reset_index(drop=True)

'''
Merge new years with old
'''
frames_carto_upload = [df_carto, df_new_years]
df_carto_upload = pd.concat(frames_carto_upload).reset_index(drop=True)

