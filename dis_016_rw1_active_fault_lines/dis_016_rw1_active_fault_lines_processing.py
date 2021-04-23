import geopandas as gpd
import os
import urllib.request
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
from zipfile import ZipFile
import logging
import datetime
import glob


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
dataset_name = 'dis_016_rw1_active_fault_lines'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://zenodo.org/record/3376300/files/GEMScienceTools/gem-global-active-faults-2019.0.zip?download=1'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'gem-global-active-faults-2019.0.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# load in the line shapefile
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, 'GEMScienceTools-gem-global-active-faults-03ad3ff/shapefile/gem_active_faults_harmonized.shp'))[0]
gdf = gpd.read_file(shapefile)

# Reproject geometries to epsg 4326
gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)

# create an index column to use as cartodb_id
gdf['cartodb_id'] = gdf.index

# reorder the columns
gdf = gdf[['cartodb_id'] + list(gdf)[:-1]]

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')

# save processed dataset to shapefile
gdf.to_file(processed_data_file, driver='ESRI Shapefile')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
# Find al the necessary components of the shapefile 
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
     for file in processed_data_files:
        zip.write(file, os.path.basename(file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))

'''
Upload processed data to Carto
'''
# upload the shapefile to Carto
util_carto.upload_to_carto(processed_data_dir, 'LINK')