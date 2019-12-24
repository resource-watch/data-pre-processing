import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'cli_064_social_cost_carbon' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cli.064_social_cost_carbon'
path = os.getenv('PROCESSING_DIR')+dataset_name
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# read in data from database of "Country-level social cost of carbon", which is the csv file "cscc_db_v2.csv" in the Github repo 
url = 'https://raw.githubusercontent.com/country-level-scc/cscc-database-2018/master/cscc_db_v2.csv' #check
df=pd.read_csv(url)

#convert table from wide form (each cscc percentile is a column) to long form (a single column of cscc percentile and a single column of cscc scores)
cscc_long = pd.melt (df, id_vars= ['run', 'dmgfuncpar', 'climate', 'SSP', 'RCP', 'N', 'ISO3', 'prtp', 'eta', 'dr'] ,value_vars=['16.7%','50%','83.3%'], var_name = 'cscc_percentile', value_name = 'cscc_score')

#convert cscc_score column from object to number
cscc_long.cscc_score = cscc_long.cscc_score.astype('float64')
#replace NaN in table with None
cscc_long=cscc_long.where((pd.notnull(cscc_long)), None)

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'.csv'
cscc_long.to_csv(csv_loc, index=False)

#Upload to Carto

#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)