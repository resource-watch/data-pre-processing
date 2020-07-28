# # RW Data Script: ocn_003_projected_sea_level_rise  
# [Metadata](https://docs.google.com/document/d/1CPGMDGpNUplVb2p3M3-mSwVrpEJz5Q_AM8x5E-iH8t8/edit)  
# [Info](https://icdc.cen.uni-hamburg.de/en/ar5-slr.html)  
# [Source](ftp://ftp-icdc.cen.uni-hamburg.de/ar5_sea_level_rise/)  
# 
# Author: Peter Kerins  
# Date: 2020 Jul 7  

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

# ### Set dataset-specific variables
# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_003_projected_sea_level_rise'

data_dict = OrderedDict()
data_dict['total_sea_level_rise'] = {
        'url': 'ftp://ftp-icdc.cen.uni-hamburg.de/ar5_sea_level_rise/total-ens-slr-85-5.nc',
        'sds': [
            'totslr',
        ],
        'missing_data': [
            1e+20,
        ],
        'pyramiding_policy': 'MEAN',
        'band_ids': ['ssh_'+str(year) for year in range(2007,2101)],
    }

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

# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# amazon storage info
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

# ## Execution

data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

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

logger.info('Creating new GeoTIFF with GEE-appropriate extent (longitude [0,360]->[-180,180])')
# in this instance, only one dataset and one file
unaligned_data_file = data_dict['total_sea_level_rise']['tifs'][0]
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')

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
cmd = cmd.format(executable, xmin, ymin, xmax, ymax, xres, yres, unaligned_data_file, processed_data_file)
completed_process = subprocess.run(cmd)
logger.debug(str(completed_process))
if completed_process.returncode!=0:
    raise Exception('Creating GeoTIFF with new extent using gdalwarp failed! Command: '+str(cmd))

logger.info('Uploading processed data to Google Cloud Storage.')
gcs_uris = util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcs_bucket)

logger.info('Uploading processed data to Google Earth Engine.')
# name bands according to variable names in original netcdf
mf_bands = util_cloud.gee_manifest_bands(data_dict, dataset_name)
pprint(mf_bands)
# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
task_id = util_cloud.gee_ingest(manifest, public=True)

util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcs_bucket)
logger.info('Files deleted from Google Cloud Storage.')

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