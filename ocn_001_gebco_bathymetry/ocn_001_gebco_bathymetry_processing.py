#Author: Kristine Lister
#Date: July 29th 2020
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
import eeUtil
from dotenv import load_dotenv
import shutil
import glob
import subprocess
import rasterio
from google.cloud import storage
import logging

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
dataset_name = 'ocn_001_gebco_bathymetry' #check
logger.info('Executing script for dataset: ' + dataset_name)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

'''
Download data and save to your data directory

Bathymetry data can be downloaded by opening the following link in your browser. 
    
https://www.bodc.ac.uk/data/open_download/gebco/gebco_2020/geotiff/

This will download a file titled 'gebco_2020_geotiff.zip' to your Downloads folder. The zip file is about 3.7 GB in size (compressed).
    
Then uncompress the data file in your downloads folder which should create a folder 'gebco_2020_geotiff'
'''
download = os.path.join(os.path.expanduser("~"), 'Downloads', 'gebco_2020_geotiff')

# Move this file into your data directory
raw_data_folder = os.path.basename(download)
shutil.move(download,raw_data_folder)


'''
Process data
Merge separate geotiffs into one file
'''
#Create list of geotiffs in data folder
geotiffs = glob.glob(os.path.join(raw_data_folder,'*.tif'))

#Read no data value from geotiff
nodata_value = -32767 #this is the nodatavalue of the geotiffs, but it will be overwritten in the next two lines
with rasterio.open(geotiffs[0]) as src:
    nodata_value = src.nodatavals[0]

#Build virtual raster file to merge geotiffs
vrt_name = '{}.vrt'.format(dataset_name)
build_vrt_command = ('gdalbuildvrt {} {}').format(vrt_name, ' '.join(geotiffs))
print('Creating vrt file to merge geotiffs')
subprocess.check_output(build_vrt_command, shell=True)

#Merge geotiffs using gdal_translate, will create merged geotiff in data folder. This will take about five minutes.
processed_data_file = '{}_edit.tif'.format(dataset_name)
gdal_translate_command = ('gdal_translate {} {} -co COMPRESS=LZW -co BIGTIFF=YES').format(vrt_name, processed_data_file)
print('Merging geotiffs')
subprocess.check_output(gdal_translate_command, shell=True)


'''
Upload processed data to Google Earth Engine
'''
# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

logger.info('Uploading processed data to Google Cloud Storage.')
gcs_uris = util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcs_bucket)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

# name bands according to variable names in original netcdf
vars = ['b0']
bands = [{'id': var, 'tileset_band_index': vars.index(var), 'pyramiding_policy': pyramiding_policy, 'missing_data': {'values': [nodata_value]}} for var in vars]

# create manifest for asset upload
manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], bands)
# upload processed data file to GEE
task_id = util_cloud.gee_ingest(manifest, public=True)
# remove files from Google Cloud Storage
util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcsBucket)
print('Files deleted from Google Cloud Storage.')

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
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))