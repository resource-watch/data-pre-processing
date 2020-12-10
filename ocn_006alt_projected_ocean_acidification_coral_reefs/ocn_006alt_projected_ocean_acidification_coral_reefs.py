#!/usr/bin/env python
# coding: utf-8

# # RW Data Script: ocn_006_projected_ocean_acidification  
# [Metadata](https://docs.google.com/document/d/17oYSsrFOFm6-ZlcEOJT6wu9VZS8FteeMuE8MgnmvVcI/edit)  
# [Info](https://coralreefwatch.noaa.gov/climate/projections/piccc_oa_and_bleaching/index.php)  
# Source files acquired directly from authors  
# 
# Author: Peter Kerins  
# Date: 2020 September 22  

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

import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import time
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
dataset_name = 'ocn_006alt_projected_ocean_acidification_coral_reefs'
logger.info('Executing script for dataset: ' + dataset_name)

# set working directory for processing dataset, and creates needed directories as necessary
data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

'''
Download data and save to your data directory
'''
# IMPORTANT: data acquired manually
# website contains some data in the kmz format, but these are not adequate for our needs
# data were acquired directly from dataset steward at noaa
# zip file was unzipped into data directory
# files included `ensemble_mean_omega_ar_rcp85.nc` (as well as equivalent for other RCPs)
# script describes subsequent processing of this file
raw_data_zip = 'data\\ocn_006_projected_ocean_acidification.zip'

'''
Process data
'''
# create dictionary for tracking info about individual variable datasets and
# their representation on google earth engine
data_dict = OrderedDict()
data_dict['aragonite_saturation'] = {
    'url': None,
    'raw_data_file': 'data\\ensemble_mean_omega_ar_rcp85.nc',
    'sds': [
        'omega_Ar',
    ],
    'missing_data': [
        -128.0,
    ],
    'pyramiding_policy': 'MEAN',
    'band_ids': ['ar_'+str(year) for year in range(2006,2100)],
}

# special dictionary for file to be used for masking
# easiest to just use the same structure
mask_dict = OrderedDict()
mask_dict['mask'] = {
    'url': None,
    'raw_data_file': 'data\\omega_Ar_year_10X_gt_8_rcp85.nc',
    'sds': [
        'reduction',
    ],
    'missing_data': [
        -128.0,
    ],
    # excluded, since will not be uploaded
#     'pyramiding_policy': 'MEAN',
#     'band_ids': ['ar_'+str(year) for year in range(2006,2100)], 
}

logger.info('Converting source NetCDF into multiband GeoTIFF')

for key, val in data_dict.items():
    val['tifs'] = util_files.convert_netcdf(val['raw_data_file'], val['sds'])

logger.info('Converting mask NetCDF into singleband GeoTIFF')

for key, val in mask_dict.items():
    val['tifs'] = util_files.convert_netcdf(val['raw_data_file'], val['sds'])

# align mask
logger.info('Creating new GeoTIFF with GEE-appropriate extent (longitude [0,360]->[-180,180])')
# in this instance, only one dataset and one file
unaligned_data_file = data_dict['aragonite_saturation']['tifs'][0]
aligned_data_file = os.path.join(data_dir,'aligned_raster'+'.tif')

# command format:
# gdalwarp -of GTiff -te <xmin> <ymin> <xmax> <ymax> -tr <xres> <yres> -t_srs EPSG:4326 <input.tif> <output.tif>
    
executable = 'gdalwarp'
xmin = -180
ymin = -90
xmax = 180
ymax = 90
xres = 1.0
yres = -1.0
cmd = '{} -of GTiff -te {} {} {} {} -tr {} {} -t_srs EPSG:4326 {} {}'
cmd = cmd.format(executable, xmin, ymin, xmax, ymax, xres, yres, unaligned_data_file, aligned_data_file)
completed_process = subprocess.run(cmd)
logger.debug(str(completed_process))
if completed_process.returncode!=0:
    raise Exception('Creating GeoTIFF with new extent using gdalwarp failed! Command: '+str(cmd))

logger.info('Creating new mask GeoTIFF with GEE-appropriate extent (longitude [0,360]->[-180,180])')
# in this instance, only one dataset and one file
unaligned_mask_file = mask = mask_dict['mask']['tifs'][0]
aligned_mask_file = os.path.join(data_dir,'aligned_mask'+'.tif')

# command format:
# gdalwarp -of GTiff -te <xmin> <ymin> <xmax> <ymax> -tr <xres> <yres> -t_srs EPSG:4326 <input.tif> <output.tif>
    
executable = 'gdalwarp'
xmin = -180
ymin = -90
xmax = 180
ymax = 90
xres = 1.0
yres = -1.0
cmd = '{} -of GTiff -te {} {} {} {} -tr {} {} -t_srs EPSG:4326 {} {}'
cmd = cmd.format(executable, xmin, ymin, xmax, ymax, xres, yres, unaligned_mask_file, aligned_mask_file)
completed_process = subprocess.run(cmd)
logger.debug(str(completed_process))
if completed_process.returncode!=0:
    raise Exception('Creating GeoTIFF with new extent using gdalwarp failed! Command: '+str(cmd))

target = aligned_data_file
mask = aligned_mask_file
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')
util_files.mask_geotiff(target, mask, processed_data_file, nodata=-128)

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
uploaded = util_cloud.aws_upload(raw_data_zip, aws_bucket, s3_prefix+os.path.basename(raw_data_zip))

logger.info('Uploading processed data to S3.')
# copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))