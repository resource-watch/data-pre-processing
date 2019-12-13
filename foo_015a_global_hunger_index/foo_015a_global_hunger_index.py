import os
import pandas as pd
import urllib.request
import tabula
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'foo_015a_global_hunger_index' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/foo_015a_global_hunger_index'
path = os.getenv('PROCESSING_DIR')+dataset_name
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Download data from the 2019 Global Hunger Index report and save to your data dir
url = 'https://www.globalhungerindex.org/pdf/en/2019.pdf' #check
file_name = data_dir+url.split('/')[-1]
urllib.request.urlretrieve(url, file_name)

# read in data from Table 2.1 GLOBAL HUNGER INDEX SCORES BY 2019 GHI RANK, which is on page 17 of the report
df=tabula.read_pdf(file_name,pages=17) #check

#remove headers and poorly formatted column names (rows 0, 1)
df=df.iloc[2:]

#get first half of table (columns 1-5, do not include rank column)
df_a=df.iloc[:, 1:6]
#name columns
col_names = ["Country", "2000", "2005", "2010", "2019"] #check
df_a.columns = col_names
#get second half of table (columns 7-11, do not include rank column) and drop empty rows at end
df_b=df.iloc[:, 7:12].dropna(how='all')
#name columns
df_b.columns = col_names

#combine first and second half of table
global_hunger_index_2019_df = pd.concat([df_a, df_b], ignore_index=True, sort=False)

# clean the dataframe
# replace <5 with 5
global_hunger_index_2019_df= global_hunger_index_2019_df.replace('<5', 5)
#replace — in table with None
global_hunger_index_2019_df = global_hunger_index_2019_df.replace({'—': None})

#convert table from wide form (each year is a column) to long form (a single column of years and a single column of values)
hunger_index_long = pd.melt (global_hunger_index_2019_df, id_vars= ['Country'] , var_name = 'year', value_name = 'hunger_index_score')

#convert year column from object to integer
hunger_index_long.year=hunger_index_long.year.astype('int64')
#convert hunger_index_score column from object to number
hunger_index_long.hunger_index_score = hunger_index_long.hunger_index_score.astype('float64')
#replace NaN in table with None
hunger_index_long=hunger_index_long.where((pd.notnull(hunger_index_long)), None)

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'.csv'
hunger_index_long.to_csv(csv_loc, index=False)

#Upload to Carto

#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)