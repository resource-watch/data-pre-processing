#!/usr/bin/env python
# coding: utf-8

# Author: Peter Kerins  
# Date: 2020 Nov 6  

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
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_012_coral_reef_tourism_value'
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
#     Supporting_Data_Rasters_And_Polys.gdb.zip
# these were downloaded and subsequently manipulated within qgis

'''
Process data
'''
# IMPORTANT: initial processing was executed manually
# qgis was used to convert vector gdb layers into shapefiles: 
#     Supporting_Data_Rasters_And_Polys MOW_Global_Coral_Tourism_Jan2017_On_Reef_Value_Poly_Equal_Area
#     Supporting_Data_Rasters_And_Polys MOW_Global_Coral_Tourism_Jan2017_Reef_Adjacent_Value_Poly_Equal_Area
#     Supporting_Data_Rasters_And_Polys MOW_Global_Coral_Tourism_Jan2017_Total_Dollar_Value_Poly_Equal_Area
#     representing, respectively: on-reef, reef-adjacent, total value
# crs was "borrowed" from another layer with correctly set metadata:
#     Supporting_Data_Rasters_And_Polys MOW_Global_Coral_Tourism_Jan2017_Total_Visitor_Equivalents_Poly
# the resulting shapefiles were placed in the data folder for further processing

# convert from vector grid to proper raster
vector_names = [
                'mow_coral-tourism_on-reef',
                'mow_coral-tourism_reef-adjacent',
                'mow_coral-tourism_total',
               ]

raster_paths = []
for name in vector_names:
    vector_path = os.path.join(data_dir,name+'.shp')
    raster_path = os.path.join(data_dir,name+'.tif')
    cmd = 'gdal_rasterize -l {} -a Value_km2 -tr 500.0 500.0 -a_nodata -128.0 -te -20037125.59408577 -3768750.9896163875 20037391.091492712 3831510.076516077 -ot Int32 -of GTiff {} {}'.format(name,vector_path,raster_path)
    completed_process = subprocess.run(cmd, shell=False)
    logger.debug(str(completed_process))
    raster_paths.append(raster_path)

logger.info('Merging relevant GeoTIFFs into final, multiband GeoTIFF for display and storage')
# this step includes some manual commands, because the default gdal tools are not robust enough
# declare name of final geotiff, and merge components
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')

cmd = 'gdalbuildvrt -separate data\\merge.vrt '+' '.join(raster_paths)
completed_process = subprocess.run(cmd, shell=False)
logger.info(completed_process)

cmd = 'gdal_translate -of GTiff data\\merge.vrt {}'.format(processed_data_file)
completed_process = subprocess.run(cmd, shell=False)
logger.info(completed_process)

# create dictionary for tracking info about individual variable datasets and
# their representation on google earth engine
data_dict = OrderedDict()
data_dict['on-reef'] = {
        'url': None,
        'missing_data': [
            -128,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': raster_paths[0],
    }
data_dict['reef-adjacent'] = {
        'url': None,
        'missing_data': [
            -128,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': raster_paths[1],
    }
data_dict['total'] = {
        'url': None,
        'missing_data': [
            -128,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': raster_paths[2],
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