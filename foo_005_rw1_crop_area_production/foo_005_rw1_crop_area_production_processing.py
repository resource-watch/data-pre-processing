import os
import sys
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
# import util_cloud
import urllib
from urllib.request import Request, urlopen
from zipfile import ZipFile
# import ee
import subprocess
# from google.cloud import storage
import logging
import requests
import json

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
dataset_name = 'foo_005_rw1_crop_area_production' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Dataset files can be downloaded at the following link:
https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PRFF8V&version=4.0
Two zipfiles were downloaded belonging to harvest and production areas were downloaded through the source's API:

Global production area: 
https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/PRFF8V/NTMZGU
Global harvest area: 
https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/PRFF8V/33PNTG
'''

url_list = ['https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/PRFF8V/NTMZGU',
            'https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/PRFF8V/33PNTG',
            'https://dataverse.harvard.edu/api/access/datafile/:persistentId/?persistentId=doi:10.7910/DVN/PRFF8V/Y1OQRN']

## Get around Harvard Dataverse blocking downloads with no User agent set.  # TODO remove for PR
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

# download the data from the source
raw_data_file = [os.path.join(data_dir, os.path.basename(url)) for url in url_list]
for url, file in zip(url_list, raw_data_file):
     urllib.request.urlretrieve(url, file)

# Unzip raw data
# Only using six crops: maize, rice, wheat, soybean, coffee (arabica and robusta), and cotton
# Only extracting the tif files that encompass all technologies (check source metadata)

# Create a list with files of interest
tif_list = [
    'spam2010V2r0_global_H_MAIZ_A.tif',
    'spam2010V2r0_global_H_RICE_A.tif',
    'spam2010V2r0_global_H_WHEA_A.tif',
    'spam2010V2r0_global_H_SOYB_A.tif',
    'spam2010V2r0_global_H_ACOF_A.tif',
    'spam2010V2r0_global_H_RCOF_A.tif',
    'spam2010V2r0_global_H_COTT_A.tif',
    'spam2010V2r0_global_P_SOYB_A.tif',
    'spam2010V2r0_global_P_WHEA_A.tif',
    'spam2010V2r0_global_P_RICE_A.tif',
    'spam2010V2r0_global_P_MAIZ_A.tif',
    'spam2010V2r0_global_P_ACOF_A.tif',
    'spam2010V2r0_global_P_RCOF_A.tif',
    'spam2010V2r0_global_P_COTT_A.tif',
    'spam2010V2r0_global_Y_MAIZ_A.tif',
    'spam2010V2r0_global_Y_RICE_A.tif',
    'spam2010V2r0_global_Y_WHEA_A.tif',
    'spam2010V2r0_global_Y_SOYB_A.tif',
    'spam2010V2r0_global_Y_ACOF_A.tif',
    'spam2010V2r0_global_Y_RCOF_A.tif',
    'spam2010V2r0_global_Y_COTT_A.tif'
]
# Create list to append location of files of interest
unzipped_list = []
# Extract files in data directory
for index, element in enumerate(raw_data_file):
    with ZipFile(raw_data_file[index], 'r') as zf:
        for file in zf.namelist():
            if file in tif_list:
                unzipped_list.append(file)
                zf.extract(file, data_dir)
# Create path to unzipped files
raw_data_file_unzipped = [os.path.join(data_dir, os.path.basename(file)) for file in unzipped_list]

'''
Process data
'''
# generate names for tif files
processed_data_files = [os.path.join(data_dir, dataset_name + '_' +file[5:])for file in raw_data_file_unzipped]
# rename the tif file
for raw, processed  in zip(raw_data_file_unzipped, processed_data_files):
    cmd = ['gdalwarp', raw, processed]
    subprocess.call(cmd)

''' # TODO remove for PR 

'''
# Upload processed data to Google Earth Engine  # TODO remove comment before PR
'''
logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storagecd 
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
# TODO Upload original data and processed data to Amazon S3 storage  # remove comment before PR
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
    for file in raw_data_file_unzipped:
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
''' # TODO remove for PR