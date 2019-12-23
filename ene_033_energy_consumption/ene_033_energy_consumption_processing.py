import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import shutil

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'ene_033_energy_consumption' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ene_033_energy_consumption'
path = os.getenv('PROCESSING_DIR')+dataset_name
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Download data and save to your data dir
'''
Country-level data for total energy consumption can be downloaded at the following link:
https://www.eia.gov/beta/international/data/browser/#/?pa=000000001&c=ruvvvvvfvtvnvv1urvvvvfvvvvvvfvvvou20evvvvvvvvvnvvuvs&ct=0&ug=4&vs=INTL.44-2-AFG-QBTU.A&cy=2017&vo=0&v=H&start=1980&end=2017

Below the map and above the data table, you will see a 'Download' button on the right side of the screen
Once you click this button, a dropdown menu will appear. Click on 'Table' under the 'Data (CSV)' section.
This will download a file titled 'International_data.csv' to your Downloads folder.
'''
download = os.path.expanduser("~")+'/Downloads/International_data.csv'

# Move this file into your data directory
csv_raw =  data_dir+dataset_name+'_raw.csv'
shutil.move(download,csv_raw)

# read in csv file as Dataframe
energy_df = pd.read_csv(csv_raw, header=[4])

#drop first column from table with no data in it
energy_df = energy_df.drop(energy_df.columns[0], axis=1)

#drop first two rows from table with no data in it
energy_df = energy_df.drop([0,1,2], axis=0)
energy_df=energy_df.reset_index(drop=True)

#rename first two unnamed columns
energy_df.rename(columns={energy_df.columns[0]:'country'}, inplace=True)
energy_df.rename(columns={energy_df.columns[1]:'unit'}, inplace=True)

#replace — in table with None
energy_df = energy_df.replace({'--': None})

#convert tables from wide form (each year is a column) to long form (a single column of years and a single column of values)
year_list = [str(year) for year in range(1980, 2018)] #check
energy_consumption_long = pd.melt (energy_df, id_vars= ['country'] ,
                                 value_vars = year_list,
                                 var_name = 'year',
                                 value_name = 'energy_consumption_quadBTU')

#convert year and value column from object to integer
energy_consumption_long.year=energy_consumption_long.year.astype('int64')
energy_consumption_long.energy_consumption_quadBTU=energy_consumption_long.energy_consumption_quadBTU.astype('float64')

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'.csv'
energy_consumption_long.to_csv(csv_loc, index=False)

#Upload to Carto

#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)