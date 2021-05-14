# Author: Rachel Thoms 
# Date: 2021 May 07
import os
import sys
import dotenv
rw_env_val = os.path.abspath(os.getenv('RW_ENV'))
dotenv.load_dotenv(rw_env_val)
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import subprocess
import shutil
from zipfile import ZipFile
from osgeo import gdal, gdal_array
import ee
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
dataset_name = 'for_031_rw0_forest_landscape_integrity_index'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# data source page:
#     https://drive.google.com/drive/folders/180DXlbF4dwCYhBW025YkZbhNHnrW5NlW
# click and download the flii_earth.tif file 

# move the data from 'Downloads' into the data directory
tifname = 'flii_earth.tif'
source_dir = os.path.join(os.getenv("DOWNLOAD_DIR"),tifname)
dest_dir = os.path.abspath(data_dir)
shutil.copy(source_dir, dest_dir)

# set name of raw data file
raw_data_file = os.path.join(data_dir,tifname)

'''
Process data
'''
# The data source multiplied the data by 1000 to store values in Integer format. 
# We need to divide the data by 1000 to obtain proper values (Range 0-10) for display on RW.

# Create file name for processed data
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')

logger.info(processed_data_file)

#Divide pixel values by 1000
cmd = ['gdal_calc.py','-A', raw_data_file, '--outfile={}'.format(processed_data_file), '--cal=A/1000.00','--NoDataValue=-9999','--type=Float32']
completed_process = subprocess.run(cmd, shell=False)
logging.debug(str(completed_process))

'''
Upload processed data to Google Earth Engine
'''

logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storage
gcs_uris = util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcsBucket )

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

# name bands according to variable names in original tif
band_ids = ['flii',
           ]

# list missing values in the original tif 
missing_values = [-9999, 
            ]
mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'missing_data': {'values': missing_values}, 'tileset_id': dataset_name,
             'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
# create manifest for asset upload
manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
# upload processed data file to GEE
task_id = util_cloud.gee_ingest(manifest, public=True)
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
renamed_raw_file = os.path.join(data_dir, dataset_name+'.zip')
shutil.copyfile(raw_data_file,renamed_raw_file)

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(renamed_raw_file, aws_bucket, s3_prefix+os.path.basename(renamed_raw_file))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
#Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
