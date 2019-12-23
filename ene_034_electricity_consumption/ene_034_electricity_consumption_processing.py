import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import shutil

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'ene_034_electricity_consumption' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ene_034_electricity_consumption'
path = os.getenv('PROCESSING_DIR')+dataset_name
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Download data and save to your data dir
'''
Country-level data for net electricity consumption can be downloaded at the following link:
https://www.eia.gov/beta/international/data/browser/#/?pa=0000002&c=ruvvvvvfvtvnvv1vrvvvvfvvvvvvfvvvou20evvvvvvvvvvvvuvs&ct=0&tl_id=2-A&vs=INTL.2-2-AFG-BKWH.A&vo=0&v=H&start=1980&end=2016

Below the map and above the data table, you will see a 'Download' button on the right side of the screen
Once you click this button, a dropdown menu will appear. Click on 'Table' under the 'Data (CSV)' section.
This will download a file titled 'International_data.csv' to your Downloads folder.
'''
download = os.path.expanduser("~")+'/Downloads/International_data.csv'

# Move this file into your data directory
csv_raw =  data_dir+dataset_name+'_raw.csv'
shutil.move(download,csv_raw)

# read in csv file as Dataframe
electricity_df = pd.read_csv(csv_raw, header=[4])

#drop first column from table with no data in it
electricity_df = electricity_df.drop(electricity_df.columns[0], axis=1)

#drop first two rows from table with no data in it
electricity_df = electricity_df.drop([0,1], axis=0)
electricity_df=electricity_df.reset_index(drop=True)

#rename first two unnamed columns
electricity_df.rename(columns={electricity_df.columns[0]:'country'}, inplace=True)
electricity_df.rename(columns={electricity_df.columns[1]:'unit'}, inplace=True)

#replace — in table with None
electricity_df = electricity_df.replace({'--': None})
electricity_df = electricity_df.replace({'-': None})

#convert tables from wide form (each year is a column) to long form (a single column of years and a single column of values)
year_list = [str(year) for year in range(1980, 2017)] #check
electricity_consumption_long = pd.melt (electricity_df, id_vars= ['country'] ,
                                 value_vars = year_list,
                                 var_name = 'year',
                                 value_name = 'electricity_consumption_billionkwh')

#convert year and value column from object to integer
electricity_consumption_long.year=electricity_consumption_long.year.astype('int64')
electricity_consumption_long.electricity_consumption_billionkwh=electricity_consumption_long.electricity_consumption_billionkwh.astype('float64')

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'.csv'
electricity_consumption_long.to_csv(csv_loc, index=False)

#Upload to Carto

#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)