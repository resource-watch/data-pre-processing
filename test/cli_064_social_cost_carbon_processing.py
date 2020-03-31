import os
import pandas as pd

# name of dataset
dataset_name = 'test_001'

# first, set the directory that you are working in with the path variable
path = '/home/user/folder_where_you_are_working'
#move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'https://raw.githubusercontent.com/country-level-scc/cscc-database-2018/master/cscc_db_v2.csv' #check

# download the data from database of "Country-level social cost of carbon", which is the csv file "cscc_db_v2.csv" in the Github repo
raw_data_file = data_dir+os.path.basename(url)
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# read in csv file as Dataframe
df=pd.read_csv(raw_data_file)

#convert table from wide form (each cscc percentile is a column) to long form (a single column of cscc percentile and a single column of cscc scores)
df_long = pd.melt (df, id_vars= ['run', 'dmgfuncpar', 'climate', 'SSP', 'RCP', 'N', 'ISO3', 'prtp', 'eta', 'dr'] ,value_vars=['16.7%','50%','83.3%'], var_name = 'cscc_percentile', value_name = 'cscc_score')

#convert cscc_score column from object to number
df_long.cscc_score = df_long.cscc_score.astype('float64')
#replace NaN in table with None
df_long=df_long.where((pd.notnull(df_long)), None)

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'_edit.csv'
df_long.to_csv(csv_loc, index=False)