# # RW Data Script: ocn_016_rw0_ocean_plastics 
# [Info](https://app.dumpark.com/seas-of-plastic-2/#)  
# [Sources](https://drive.google.com/file/d/0B4XxjklEZhMtOEVHLXc1WlM5Wm8/view)  
# 
# Author: Kristine Lister 
# Date: 2020 Dec 21

# ### Import

import os
import sys
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))
utils_path = os.path.join(os.getenv('PROCESSING_DIR'),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import time
import logging
from pprint import pprint
from collections import OrderedDict 
# dataset-specific imports
import datetime
import numpy as np
import glob
from osgeo import gdal

# ### Set dataset-specific variables

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_016_rw0_ocean_plastics'

#Download url
url = 'https://drive.google.com/u/0/uc?id=0B4XxjklEZhMtOEVHLXc1WlM5Wm8&export=download'

#Raw data file name
raw_data_file = 'ocn_016_rw0_ocean_plastics.zip'


# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
logger.info('Data directory relative path: '+data_dir)
logger.info('Data directory absolute path: '+os.path.abspath(data_dir))
'''
Download data and save to your data directory
'''
# switch to data directory
os.chdir(data_dir)

# remove any files in data directory
for temp_file in glob.glob('*'):
    os.remove(temp_file)

# download zip file containing data
logger.info('Downloading raw data')
util_files.download_file_from_google_drive('0B4XxjklEZhMtOEVHLXc1WlM5Wm8',url,raw_data_file)
logger.info('Raw data file path: ' + raw_data_file)

# extract data into data directory
logger.info('Extracting relevant GeoTIFFs from source zip file')
with ZipFile(raw_data_file, 'r') as zip_ref:
    zip_ref.extractall()

# get a list of all the raw files
data_files = glob.glob('*.tif')

# loop through the files to get the no-data value and shift from 0 to 360 longitude to -180 to 180 longitude
data_dict = {}
for data_file in data_files:
    # open dataset to get minimum data value, which is the no-data value
    ds = gdal.Open(data_file)
    # read band data
    band = ds.GetRasterBand(1)
    # get minimum and maximum statistics
    stats = band.ComputeRasterMinMax()
    # minimum is the first one, set that as nodata
    nodata = stats[0]
    # set a new file name to represent processed data
    new_data_file = data_file.replace('_360','')
    # run command to shift longitude and set no-data value
    cmd = 'gdalwarp -s_srs "+proj=longlat +ellps=WGS84" -t_srs WGS84 -dstnodata {} -overwrite -wo SOURCE_EXTRA=1000 --config CENTER_LONG 0 {} {}'.format(nodata,data_file,new_data_file)
    completed_process = subprocess.check_output(cmd, shell=True)
    # set data dictionary to have keys as the new data file name and values as the no-data values
    data_dict[new_data_file] = nodata
    

'''
Upload processed data to Google Earth Engine
'''

logger.info('Uploading processed data to Google Cloud Storage and Google Earth Engine.')
# set up Google Cloud Storage project and bucket objects
text_file = open("gcsPrivateKey.json", "w")
n = text_file.write(os.getenv('GEE_JSON'))
text_file.close()
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# initialize ee module for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# loop through data files in data_dict
for data_file in data_dict.keys():
    # set image name as basename of the file
    image_name = os.path.basename(data_file.split('.')[0])
    # upload to google cloud
    gcs_uris = util_cloud.gcs_upload(data_file, image_name, gcs_bucket=gcsBucket)
    # define asset name 
    asset_name = 'projects/resource-watch-gee/{}/{}'.format(dataset_name,image_name)
    # define band dictionary for manifest upload, with the missing data, b1 as band name, and pyramiding pollicy as mean
    upload_data_dict = OrderedDict()
    upload_data_dict[image_name] = {
            'missing_data': [
                data_dict.get(data_file),
            ],
            'pyramiding_policy': 'MEAN',
            'band_ids':[
                'b1'
            ]
        }
    # upload to google earth engine
    mf_bands = util_cloud.gee_manifest_bands(upload_data_dict, dataset_name=image_name)
    manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
    task_id = util_cloud.gee_ingest(manifest, public=False)
    # remove from google cloud storage
    util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcsBucket)

'''
Upload original data and processed data to Amazon S3 storage
'''

# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'
logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
uploaded = util_cloud.aws_upload(raw_data_file, aws_bucket, s3_prefix+os.path.basename(raw_data_file))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    for processed_data_file in data_dict.keys():
        zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
