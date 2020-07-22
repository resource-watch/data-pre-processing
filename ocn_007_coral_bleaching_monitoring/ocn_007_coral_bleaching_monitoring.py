# # RW Data Script: ocn_007_coral_bleaching_monitoring  
# [Info](https://coralreefwatch.noaa.gov/product/5km/index.php)  
# [Sources](ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/)  
# 
# Author: Peter Kerins  
# Date: 2020 Jun 23  

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
import time
import logging
from pprint import pprint
from collections import OrderedDict 
# dataset-specific imports
import datetime
import numpy as np

# ### Set dataset-specific variables

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_007_coral_bleaching_monitoring'

# this dataset requires acquiring several separate netcdf files
# file path examples:
# baa:  ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/baa-max-7d/2020/ct5km_baa-max-7d_v3.1_20200623.nc
# hs:   ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/hs/2020/ct5km_hs_v3.1_20200622.nc
# dhw:  ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/dhw/2020/ct5km_dhw_v3.1_20200622.nc
# ssta: ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/ssta/2020/ct5km_ssta_v3.1_20200622.nc
# sst:  ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/coraltemp/v1.0/nc/2020/coraltemp_v1.0_20200622.nc
# sstt: ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/sst-trend-7d/2020/ct5km_sst-trend-7d_v3.1_20200622.nc

# note that all netcdfs contain a "mask" subdataset, but it is the same for each so does not need to be extracted
data_dict = OrderedDict()
data_dict['bleaching_alert_area_7d'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/baa-max-7d/{}/ct5km_baa-max-7d_v3.1_{}.nc',
        'sds': [
            'bleaching_alert_area',
        ],
        'missing_data': [
            -5,
            251,
        ],
        'pyramiding_policy': 'MEAN',
    }
data_dict['hotspots'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/hs/{}/ct5km_hs_v3.1_{}.nc',
        'sds': [
            'hotspot',
        ],
        'missing_data': [
            -32768,
        ],
        'pyramiding_policy': 'MEAN',
        'scale_factor': 0.0099999998,
    }
data_dict['degree_heating_week'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/dhw/{}/ct5km_dhw_v3.1_{}.nc',
        'sds': [
            'degree_heating_week',
        ],
        'missing_data': [
            -32768,
        ],
        'pyramiding_policy': 'MEAN',
        'scale_factor': 0.0099999998,
    }
data_dict['sea_surface_temperature_anomaly'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/ssta/{}/ct5km_ssta_v3.1_{}.nc',
        'sds': [
            'sea_surface_temperature_anomaly',
        ],
        'missing_data': [
            -32768,
        ],
        'pyramiding_policy': 'MEAN',
        'scale_factor': 0.0099999998,
    }
data_dict['sea_surface_temperature'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/coraltemp/v1.0/nc/{}/coraltemp_v1.0_{}.nc',
        'sds': [
            'analysed_sst',
        ],
        'missing_data': [
            -32768,
        ],
        'pyramiding_policy': 'MEAN',
        'scale_factor': 0.01,
    }
data_dict['sea_surface_temperature_trend_7d'] = {
        'url_template': 'ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/5km/v3.1/nc/v1.0/daily/sst-trend-7d/{}/ct5km_sst-trend-7d_v3.1_{}.nc',
        'sds': [
            'trend',
        ],
        'missing_data': [
            -32768,
        ],
        'pyramiding_policy': 'MEAN',
        'scale_factor': 0.0099999998,
    }


# baa original: -5=No Data (land); 0=No Stress; 1=Watch; 2=Warning; 3=Alert Level 1; 4=Alert Level 2
#     valid range [0,4]
#     fill value -5
#     scalefactor = 1
# hs original: from low negatives up to about 10(C). scale bar from 0-5. nodata=nodata(land)
#     valid range [-1500,1500]
#     fill value -32768
#     scalefactor = 0.0099999998
# dhw original
#     valid range [0,10000]
#     fill value -32768
#     scalefactor = 0.0099999998
# sst anomaly
#     valid range [-1500,1500]
#     fill value -32768
#     scalefactor = 0.0099999998
# sst
#     valid range [-200,5000]
#     fill value -32768
#     scale_factor=0.01
# sst trend
#     valid range [-1500,1500]
#     fill value -32768
#     scale_factor=0.0099999998


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

# create request urls
# previous day's data appears on server just before 11am (ET?)
now = datetime.datetime.now()
now_hour = int(now.strftime('%H'))

if now_hour >= 11:
    logger.info('Targeting data from yesterday (script running after 11am)')
    target_date = now - datetime.timedelta(days=1)
else:
    logger.info('Targeting data from day before yesterday (script running before 11am)')
    target_date = now - datetime.timedelta(days=2)

target_year = target_date.strftime('%Y')
target_date = target_date.strftime('%Y%m%d')
# can manual override date to test script when server is not updating
target_year = '2020'
target_date = '20200623'

for key, val in data_dict.items():
    val['url'] = val['url_template'].format(target_year, target_date)

logger.info('Downloading raw data')
for key, val in data_dict.items():
    url = val['url']
    raw_data_file = os.path.join(data_dir,os.path.basename(url))
    urllib.request.urlretrieve(url, raw_data_file)
    val['raw_data_file'] = raw_data_file
    logger.debug('('+key+')'+'Raw data file path: ' + raw_data_file)

logger.info('Extracting relevant GeoTIFFs from source NetCDFs')
for key, val in data_dict.items():
    val['tifs'] = util_files.convert_netcdf(val['raw_data_file'], val['sds'])

# no masking necessary, in theory
# do need to scale most of the datasets though
alltifs = []
for key, val in data_dict.items():
    if 'scale_factor' in val and float(val['scale_factor'] != 1.0):
        finaltifs = []
        for tif in val['tifs']:
            finaltifs.append(util_files.scale_geotiff(tif))
    else:
        finaltifs = val['tifs']
    val['finaltifs'] = finaltifs
    alltifs.extend(finaltifs)

logger.info('Merging masked, single-band GeoTIFFs into single, multiband GeoTIFF.')
multitif = os.path.abspath(os.path.join(data_dir,dataset_name+'.tif'))
util_files.merge_geotiffs(alltifs, multitif, ot='float32')
processed_data_file = multitif

logger.info('Uploading processed data to Google Cloud Storage.')
gcs_uris = util_cloud.gcs_upload(multitif, dataset_name, gcs_bucket=gcs_bucket)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee module for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# name bands according to variable names in original netcdf
mf_bands = util_cloud.gee_manifest_bands(data_dict, dataset_name)
# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
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
    for key, val in data_dict.items():
        raw_data_file = val['raw_data_file']
        zip.write(raw_data_file, os.path.basename(raw_data_file))
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
