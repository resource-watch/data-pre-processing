import shutil
import glob
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import logging
from ftplib import FTP
import urllib
import numpy as np
import pandas as pd
from shapely.geometry import Point 
import geopandas as gpd 
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
dataset_name = 'dis_017_storm_events_US' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory.
Two types of files are being used: details and locations.
Using bulk download via FTP, link to NOAA's storm events database:
https://www.ncdc.noaa.gov/stormevents/ftp.jsp
'''
# connect to the FTP server and login anonymously
ftp = FTP('ftp.ncdc.noaa.gov', timeout = 30)
ftp.login()
# navigate to the correct directory and get a list of all filenames
ftp.cwd('/pub/data/swdi/stormevents/csvfiles/')
filenames = ftp.nlst()

# retrieve a sorted list of the details files for events since year_min
details_files = []
year_min = 1950
for filename in filenames:
    if not filename.startswith('StormEvents_details-ftp_v1.0_d'):
        continue
    if int(filename[30:34]) >= year_min:
        details_files.append(filename)
details_files.sort()

# retrieve a sorted list of the locations files since year_min
locations_files = []
year_min = 1950
for filename in filenames:
    if not filename.startswith('StormEvents_locations-ftp_v1.0_d'):
        continue
    if int(filename[32:36]) >= year_min:
        locations_files.append(filename)
locations_files.sort()

#Downloading data function
def ftp_download(file_dir):
    for filename in file_dir:
     with open(filename, 'wb') as fo:
        ftp.retrbinary("RETR " + filename, fo.write)
#We download data from the source FTP
ftp_download(details_files)
ftp_download(locations_files)

#Moving all files inside data folder
sourcepath= os.getcwd()
sourcefiles = os.listdir(sourcepath)
destinationpath = r'data'
for file in sourcefiles:
    if file.endswith(".gz"):
        shutil.move(os.path.join(sourcepath,file), os.path.join(destinationpath,file))

#Creating function to create directory for processed data 
def dir_mkr(directory_name):
    path = sourcepath + '/' + directory_name
    try:
        os.mkdir(path)
    except OSError:
     print ("Creation of the directory %s failed" % path)
    else:
     print ("Successfully created the directory %s " % path) 

#Creating directory for processed data)
dir_mkr('processed_data_dir')
'''
Process data
'''
#Concatenating details and locations files

all_files = glob.glob(os.path.join(destinationpath, "*.gz"))     # advisable to use os.path.join as this makes concatenation OS independent

details_list = []
locations_list = []

for file in all_files:
    if file.startswith('data/StormEvents_details-ftp_v1.0_d'):
        df = pd.read_csv(file)
        details_list.append(df)
        #details_concatenated  = pd.concat(df, ignore_index=True)
    elif file.startswith('data/StormEvents_locations-ftp_v1.0_d'):
        df_1 = pd.read_csv(file)
        #locations_concatenated  = pd.concat(df_1, ignore_index=True)
        locations_list.append(df_1)
    else: print('error')
    
details_concatenated = pd.concat(details_list, ignore_index=True)
locations_concatenated = pd.concat(locations_list, ignore_index=True)

##Selecting columns of interest from dataset and Cleaning locations dataset
event_details = details_concatenated[['EVENT_ID', "YEAR", "EVENT_TYPE", "BEGIN_LAT","BEGIN_LON","END_LAT","END_LON"]]
event_locations = locations_concatenated[['EVENT_ID', "LOCATION", "LATITUDE", "LONGITUDE"]]
event_locations = event_locations.replace(to_replace="\s\s*",value = '',regex=True)
#Merging details and details files 'EVENT_ID' and changing column names to lowercase
events = pd.merge(event_details, event_locations, on='EVENT_ID')
events.columns= events.columns.str.strip().str.lower()
# creating a geometry column 
geometry = [Point(xy) for xy in zip(events['latitude'], events['longitude'])]
# Coordinate reference system : WGS84
crs = {'init': 'epsg:4326'}
# Creating a Geographic data frame 
gdf = gpd.GeoDataFrame(events, crs=crs, geometry=geometry)
#Exporting to csv
gdf.to_csv('processed_data_dir/dis_017_storm_events_US.csv', index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto('processed_data_dir/dis_017_storm_events_US.csv', 'LINK')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
shutil.make_archive('raw_data', 'zip', 'data')
raw_data = os.path.join(sourcepath, 'raw_data'+'.zip')
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data, aws_bucket, s3_prefix+os.path.basename(raw_data))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
shutil.make_archive('processed_data', 'zip', 'processed_data_dir')
processed_data = os.path.join(sourcepath, 'processed_data'+'.zip')
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data, aws_bucket, s3_prefix+os.path.basename(processed_data))


