#!/usr/bin/env python
# coding: utf-8

# # RW Data Script: ocn_011_total_suspended_matter  
# [Metadata](https://docs.google.com/document/d/1wmz4IQLh5O35NctTFZhXXfe-HpVa036g4EFPsdy_DZM/edit)  
# [Info](https://www.globcolour.info/products_description.html)  
# [Source](ftp://ftp.hermes.acri.fr/GLOB/olcib/) (registration & FTP client required)
# 
# Author: Peter Kerins  
# Date: 2020 Dec 11    

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

# dataset-specific imports
import datetime
import calendar
import numpy as np
from shutil import copyfile

# ### Set dataset-specific variables

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_011_total_suspended_matter'
# set working directory for processing dataset, and creates needed directories as necessary
data_dir = util_files.prep_dirs(dataset_name)

# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.DEBUG)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger.info('Executing script for dataset: ' + dataset_name)

data_dict = OrderedDict()
data_dict['tsm_month'] = {
        # basic path: ftp://ftp.hermes.acri.fr/GLOB/olcib/month/2020/11/01/L3m_20201101-20201130__GLOB_4_AV-OLB_TSM_MO_00.nc
        # splitting into two pieces for login-required ftp
        # dir template items: username, password, year (YYYY), month (mm),  first day of month (YYYYmmdd), last day of month (YYYYmmdd)
        'url_template': 'ftp://{}:{}@ftp.hermes.acri.fr/GLOB/olcib/month/{}/{}/01/L3m_{}-{}__GLOB_4_AV-OLB_TSM_MO_00.nc',
        'sds': [
            'TSM_mean',
        ],
        'original_nodata': -999,
        'missing_data': [
            -999,
        ],
        'pyramiding_policy': 'MEAN',
    }

# create request url
ftp_username= os.environ.get('GLOBCOLOUR_USERNAME')
ftp_password= os.environ.get('GLOBCOLOUR_PASSWORD')

today = datetime.datetime.now()
firstofmonth = today.replace(day=1)
lastmonth = firstofmonth - datetime.timedelta(days=1)
monthrange = calendar.monthrange(lastmonth.year, lastmonth.month)

dt_start = datetime.datetime(lastmonth.year,lastmonth.month,1)
dt_end = datetime.datetime(lastmonth.year,lastmonth.month,monthrange[1])

reqyear = str(lastmonth.year)
reqmonth = str(lastmonth.month)
reqstart = dt_start.strftime('%Y%m%d')
reqend = dt_end.strftime('%Y%m%d')

data_dict['tsm_month']['url'] = data_dict['tsm_month']['url_template'].format(ftp_username,ftp_password,reqyear,reqmonth,reqstart,reqend)

logger.info('Downloading raw data')

for key, val in data_dict.items():
    # urllib template: urllib.urlretrieve('ftp://username:password@server/path/to/file', 'file')
    url = val['url']
    raw_data_file = os.path.join(data_dir,os.path.basename(url))
    urllib.request.urlretrieve(url, raw_data_file)
    val['raw_data_file'] = raw_data_file
    logger.debug('('+key+')'+'Raw data file path: ' + raw_data_file)

logger.info('Extracting relevant GeoTIFFs from source NetCDFs')

for key, val in data_dict.items():
    val['tifs'] = util_files.convert_netcdf(val['raw_data_file'], val['sds'])

# there will be additional steps if script is changed to grab 8day as well as monthly tsm
# for now its straightforward because no tif reprocessing is necessary
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')
copyfile(data_dict['tsm_month']['tifs'][0], processed_data_file)

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