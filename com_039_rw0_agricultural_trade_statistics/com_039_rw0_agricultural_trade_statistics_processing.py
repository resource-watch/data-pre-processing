import pandas as pd
import requests
import os
import sys
import io
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import logging

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers:
   logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'com_039_rw0_agricultural_trade_statistics'

logger.info('Executing script for dataset: ' + dataset_name)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''

# insert the url used to download the data from the source website
url = 'https://fenixservices.fao.org/faostat/api/v1/en/data/TCL?area=5000%3E&area_cs=FAO&element=2910%2C2920%2C2610%2C2620&item=656%2C657%2C767%2C768%2C28%2C27&item_cs=FAO&year=1990%2C1991%2C1992%2C1993%2C1994%2C1995%2C1996%2C1997%2C1998%2C1999%2C2000%2C2001%2C2002%2C2003%2C2004%2C2005%2C2006%2C2007%2C2008%2C2009%2C2010%2C2011%2C2012%2C2013%2C2014%2C2015%2C2016%2C2017%2C2018%2C2019%2C2020&show_codes=true&show_unit=true&show_flags=true&show_notes=true&null_values=false&output_type=csv'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# get data from url
raw_data = requests.get(url).content

# read the raw data into a pandas dataframe
df = pd.read_csv(io.StringIO(raw_data.decode(encoding='utf-8')))

# create a path to the raw data file, then save to csv
raw_data_file = os.path.join(data_dir, 'TCL.csv')
df.to_csv(raw_data_file, index=False)

'''
Process data
'''
# convert column names to lowercase
df.columns = [x.lower() for x in df.columns]

# rename "area" column to "country" for compliance with Carto Table
df.rename(columns={'area': 'country'}, inplace=True)

# remove parentheses in column headers
df.columns = df.columns.str.replace('[()]', '', regex=True)

# add underscores between words in column headers
df.columns = df.columns.str.replace(' ', '_')

# create a new column 'datetime' to store years as datetime objects
df['datetime'] = [datetime(x, 1, 1) for x in df.year]

# replace all NaN with None
df = df.where((pd.notnull(df)), None)

# save processed dataset to CSV
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)
