import requests
import zipfile
import pandas as pd
import io
from io import StringIO
import urllib
import os
import sys
import dotenv
dotenv.load_dotenv('C:\\Users\\Jason.Winik\\OneDrive - World Resources Institute\\Documents\\GitHub\\cred\\.env')
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
gdal_path = os.getenv('GDAL_DIR')
if gdal_path not in sys.path:
    sys.path.append(gdal_path)
import gdal
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import logging

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
dataset_name = 'cli_017_rw1_glacier_locations' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')

#download the data from the source
url = "https://www.glims.org/download/latest"
raw_data_file = os.path.join(data_dir,os.path.basename(url)+'.zip')
r = urllib.request.urlretrieve(url, raw_data_file)
# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

# read in data to pandas dataframe
r = requests.get(url)
df = pd.read_csv(io.BytesIO(r.content), encoding='utf8', header=None)

# save unprocessed source data to put on S3 (below)
raw_data_file = os.path.join(data_dir, os.path.basename(url))
df.to_csv(raw_data_file, header = False, index = False)

