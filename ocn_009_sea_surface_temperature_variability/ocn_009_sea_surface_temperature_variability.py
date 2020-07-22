#!/usr/bin/env python
# coding: utf-8

# # RW Data Script: ocn_009_sea_surface_temperature_variability
# [Info](https://coralreefwatch.noaa.gov/product/thermal_history/sst_variability.php)  
# [Source](ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/thermal_history/v2.1)  
# 
# Author: Peter Kerins  
# Date: 2020 Jun 18  

# ### Import

import os
import sys
import dotenv
dotenv.load_dotenv(os.path.abspath(os.getenv('RW_ENV')))
if os.getenv('PROCESSING_DIR') not in sys.path:
    sys.path.append(os.path.abspath(os.getenv('PROCESSING_DIR')))
import util_files
import util_cloud
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
from shutil import copyfile
import time
import logging


# ### Set dataset-specific variables

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_009_sea_surface_temperature_variability'

# netcdf subdatasets that will be used in processing
subdatasets = ['stdv_maxmonth',
               'stdv_annual',
               'mask',
              ]

# nedcdf subdatasets that will be uploaded as bands to GEE
band_ids = ['stdv_maxmonth',
            'stdv_annual',
           ]
# ### Set/initialize/authenticate general variables

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
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))
logger.info('Downloading raw data')

url='ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/thermal_history/v2.1/noaa_crw_thermal_history_sst_variability_v2.1.nc'
raw_data_file = os.path.join(data_dir,os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

logger.debug('Raw data file path: ' + raw_data_file)

logger.info('Extracting relevant GeoTIFFs from source NetCDF')

tifs = util_files.convert_netcdf(raw_data_file, subdatasets)

logger.info('Mask extracted GeoTIFFs using dataset mask')
# create dict linking subdatasets from the netcdf to the geotiffs that now contain each
sds_file_dict=dict(zip(subdatasets,tifs))
# set nodata value for masking
nodata=-128

# cycle through target tifs (corresponding to bands) and mask them with mask tif
masked_tifs = []
for band_id in band_ids:
    sds_file = sds_file_dict[band_id]
    band_masked = sds_file[:sds_file.find('.tif')] + '_masked.tif'
    util_files.mask_geotiff(sds_file_dict[band_id], sds_file_dict['mask'], band_masked, nodata=nodata)
    masked_tifs.append(band_masked)
    
logger.info('Merge masked, single-band GeoTIFFs into single, multiband GeoTIFF.')
# merge multiple masked single-band tifs as layers in single multiband tif
multitif = os.path.abspath(os.path.join(data_dir,dataset_name+'.tif'))
util_files.merge_geotiffs(masked_tifs, multitif)
processed_data_file = multitif

'''
Upload processed data to Google Earth Engine
'''

logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

gcs_uris= util_cloud.gcs_upload(multitif, dataset_name, gcs_bucket=gcsBucket)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check
           
# name bands according to variable names in original netcdf
mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': dataset_name, 'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'
manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
task_id = util_cloud.gee_ingest(manifest, public=True)

task_id = util_cloud.gee_ingest(manifest, public=True)

util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcs_bucket)
logger.info('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''

# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'
logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
