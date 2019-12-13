import os
import pandas as pd
import zipfile
import urllib.request
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'ene_021a_renewable_energy_consumption' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ene_021a_renewable_energy_consumption'
path = os.getenv('PROCESSING_DIR')+dataset_name
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

# Download data and save to your data dir
url = 'http://databank.worldbank.org/data/download/SE4ALL_csv.zip'#check
file_name = data_dir+url.split('/')[-1]
urllib.request.urlretrieve(url, file_name)

#unzip source data
zip_ref = zipfile.ZipFile(file_name, 'r')
zip_ref.extractall(file_name.split('.')[0])
zip_ref.close()

# read in csv file as Dataframe 
energy_df = pd.read_csv(file_name.split('.')[0]+'/SE4ALLData.csv')

# subset for renewable energy consumption data 
renewable_energy_df = energy_df[energy_df['Indicator Name'].str.contains('Renewable energy consumption')]

#convert tables from wide form (each year is a column) to long form (a single column of years and a single column of values)
renewable_energy_long = pd.melt (renewable_energy_df, id_vars= ['Country Name' ,'Country Code'] , 
                                 value_vars = ['1990', '1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016'],
                                 var_name = 'year',
                                 value_name = 'renewable energy consumption')

#convert year column from object to integer
renewable_energy_long.year=renewable_energy_long.year.astype('int64')

#save processed dataset to csv
csv_loc = data_dir+dataset_name+'.csv'
renewable_energy_long.to_csv(csv_loc, index=False)

#Upload to Carto

#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#upload dataset to carto
dataset = dataset_manager.create(csv_loc)