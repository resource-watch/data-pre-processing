# Author: Peter Kerins  
# Date: 2020 Jul 15  

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
dataset_name = 'ocn_010_projected_coral_bleaching'
logger.info('Executing script for dataset: ' + dataset_name)

data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

'''
Download data and save to your data directory
'''
# IMPORTANT: data downloaded manually
# .lpk file (ArcGis layer package) url:
#     https://coralreefwatch.noaa.gov/climate/projections/downscaled_bleaching_4km/van_Hooidonk_et_al._Downscaled_Bleaching_Projections.lpk
# layer package was opened in ArcMap, and then the component layers were simply saved as GeoTIFF files:
#     dw_year_2X_gt_8_ensemble_rcp45.tif, dw_year_10X_gt_8_ensemble_rcp45.tif, 
#     mean_year_2X_gt_8_ensemble_rcp85.tif, mean_year_10X_gt_8_ensemble_rcp85.tif, reefs_mask.tif
# these were placed in the data folder

'''
Process data
'''
# create dictionary for tracking info about individual variable datasets and
# their representation on google earth engine
data_dict = OrderedDict()
data_dict['per_decade_2x'] = {
        'url': 'https://coralreefwatch.noaa.gov/climate/projections/downscaled_bleaching_4km/van_Hooidonk_et_al._Downscaled_Bleaching_Projections.lpk',
        'missing_data': [
            0, 2147483647,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': 'data\\mean_year_2X_gt_8_ensemble_rcp85.tif',
    }
data_dict['per_decade_10x'] = {
        'url': 'https://coralreefwatch.noaa.gov/climate/projections/downscaled_bleaching_4km/van_Hooidonk_et_al._Downscaled_Bleaching_Projections.lpk',
        'missing_data': [
            0, 2147483647,
        ],
        'pyramiding_policy': 'MEAN',
        'raw_data_file': 'data\\mean_year_10X_gt_8_ensemble_rcp85.tif',
    }

# make list of all tifs to be combined
alltifs = []
for key, val in data_dict.items():
    alltifs.append(val['raw_data_file'])

logger.info('Merging relevant GeoTIFFs into final, multiband GeoTIFF for display and storage')
# declare name of final geotiff, and merge components
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')
util_files.merge_geotiffs(alltifs, processed_data_file)

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
with ZipFile(raw_data_dir,'w') as zip:
    for key, val in data_dict.items():
        raw_data_file = val['raw_data_file']
        zip.write(raw_data_file, os.path.basename(raw_data_file))
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))