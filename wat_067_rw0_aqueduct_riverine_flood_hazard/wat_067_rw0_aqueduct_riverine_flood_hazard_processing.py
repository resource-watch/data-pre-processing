import os
import sys
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
import logging


# Set up logging
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
dataset_name = 'wat_067_rw0_aqueduct_riverine_flood_hazard' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
Data can be downloaded at the following link:
http://wri-projects.s3.amazonaws.com/AqueductFloodTool/download/v2/index.html

Four files that were downloaded under the RCP 8.5 scenario, 
GFDL-ESM2M model, and a flood magnitude of 100 years: 
    Baseline Riverine Flood
    2030 Riverine Flood
    2050 Riverine Flood
    2080 Riverine Flood
'''

# list the urls used to download the data from the source website
url_list = [
    'http://wri-projects.s3.amazonaws.com/AqueductFloodTool/download/v2/inunriver_historical_000000000WATCH_1980_rp00100.tif',
    'http://wri-projects.s3.amazonaws.com/AqueductFloodTool/download/v2/inunriver_rcp8p5_0000GFDL-ESM2M_2030_rp00100.tif',
    'http://wri-projects.s3.amazonaws.com/AqueductFloodTool/download/v2/inunriver_rcp8p5_0000GFDL-ESM2M_2050_rp00100.tif',
    'http://wri-projects.s3.amazonaws.com/AqueductFloodTool/download/v2/inunriver_rcp8p5_0000GFDL-ESM2M_2080_rp00100.tif']


# download the data from the source
raw_data_file = [os.path.join(data_dir,os.path.basename(url)) for url in url_list]
for url, file in zip(url_list, raw_data_file):
     urllib.request.urlretrieve(url, file)
     

'''
Process data
'''
# generate names
# the data contained in the 1980 geotiff is mislabeled by the source
# the 1980 geotiff is actually data for 2010 
# for questions about these geotiffs please contact Liz Saccoccia at elizabeth.saccoccia@wri.org.
processed_data_files = [os.path.join(data_dir, dataset_name + file[-17:-12] + '.tif') if '1980' not in file else os.path.join(data_dir, dataset_name + '_2010' + '.tif') for file in raw_data_file ]
 

# rename the tif file
for raw, processed  in zip(raw_data_file, processed_data_files) :
    cmd = ['gdalwarp', raw, processed]
    subprocess.call(cmd)

'''
Upload processed data to Google Earth Engine
'''
logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storage
gcs_uris= util_cloud.gcs_upload(processed_data_files, dataset_name, gcs_bucket=gcsBucket)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Create an image collection where we will put the processed data files in GEE
image_collection = f'projects/resource-watch-gee/{dataset_name}'
ee.data.createAsset({'type': 'ImageCollection'}, image_collection)

# set image collection's privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(image_collection, acl)
print('Privacy set to public.')

# list the bands in each image
band_ids = ['b1']

task_id = []
# Upload processed data files to GEE
for uri in gcs_uris:
    # generate an asset name for the current file by using the filename (minus the file type extension)
    asset_name = f'projects/resource-watch-gee/{dataset_name}/{os.path.basename(uri)[:-4]}'
    # create the band manifest for this asset
    mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': os.path.basename(uri)[:-4],
             'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
    # create complete manifest for asset upload
    manifest = util_cloud.gee_manifest_complete(asset_name, uri, mf_bands)
    # upload the file from GCS to GEE
    task = util_cloud.gee_ingest(manifest)
    print(asset_name + ' uploaded to GEE')
    task_id.append(task)

# remove files from Google Cloud Storage
util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcsBucket)
logger.info('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

logger.info('Uploading original data to S3.')
# Upload raw data file to S3

print('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_files:
        zipped.write(file, os.path.basename(file))

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
