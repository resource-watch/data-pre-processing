#!/usr/bin/env python
# coding: utf-8

# # RW Data Script: ocn_014_index_of_coastal_protection_by_coral_reefs  
# [Metadata](https://docs.google.com/document/d/1IHZYUIh25JGZtx2k1ItTYvPA435PzIvoqCxzXjoEPzc/edit)  
# [Info](http://maps.oceanwealth.org/)  
# ~Source~  
# 
# Author: Peter Kerins  
# Date: 2020 Nov 11  

# ### Import

import os
import sys
import dotenv
dotenv.load_dotenv(os.path.abspath(os.getenv('RW_ENV')))
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud

import subprocess
import urllib
from zipfile import ZipFile
import ee
from google.cloud import storage
import logging
from pprint import pprint
from collections import OrderedDict 

# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.DEBUG)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_014_index_of_coastal_protection_by_coral_reefs'
logger.info('Executing script for dataset: ' + dataset_name)

# set working directory for processing dataset, and creates needed directories as necessary
data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

'''
Download data and save to your data directory
'''
# IMPORTANT: data downloaded manually
# zipped geodatabase provided by dataset steward at tnc:
#     MOW_Coral_Reef_ES_Data.gdb.zip
# this was downloaded and subsequently manipulated within qgis

'''
Process data
'''
# IMPORTANT: initial processing was executed manually
# qgis was used to convert vector gdb layer into shapefile: 
#     MOW_Coral_Reef_ES_Data MOW_Global_Coral_Protection_dis
# the resulting shapefile was placed in the data folder for further processing

# convert from vector grid to proper raster
vector_names = [
                'mow_coastal-protection-index',
               ]

# rasterize data
# gdal bytes are unsigned so nodata value is 0
vector_path = os.path.join(data_dir,vector_names[0]+'.shp')
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')

cmd = 'gdal_rasterize -l {} -a GRIDCODE -tr 500.0 500.0 -a_nodata 0 -te -20037125.59408577 -3768750.9896163875 20037391.091492712 3831510.076516077 -ot Byte -of GTiff {} {}'.format(vector_names[0],vector_path,processed_data_file)
completed_process = subprocess.run(cmd, shell=False)
logger.debug(str(completed_process))

# create dictionary for tracking info about individual variable datasets and
# their representation on google earth engine
data_dict = OrderedDict()
data_dict['coastal-protection'] = {
        'url': None,
        'missing_data': [
            0,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': processed_data_file,
    }

'''
Upload processed data to Google Earth Engine
'''
# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# initialize ee (Google Earth Engine Python API) for uploading to GEE
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

logger.info('Uploading processed data to Google Cloud Storage.')
gcs_uris = util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcs_bucket)

logger.info('Uploading processed data to Google Earth Engine.')
# generate bands component of GEE upload manifest
mf_bands = util_cloud.gee_manifest_bands(data_dict, dataset_name)
# upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
logger.debug(manifest)
task_id = util_cloud.gee_ingest(manifest, public=True)

util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcs_bucket)
logger.info('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''
# amazon storage info
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

logger.info('Uploading original data to S3.')
# copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))