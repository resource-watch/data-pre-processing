import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import urllib
import zipfile
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import logging


# set up logging
# get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'wat_039_rw0_wetlands' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://c402277.ssl.cf1.rackcdn.com/publications/18/files/original/GLWD-level3.zip?1343838716'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'GLWD-level3.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process data
'''
# convert the ESRI Grid file to GeoTIFF file and set coordinate system
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.tif')
cmd = ['gdal_translate','-a_srs','EPSG:4326',raw_data_file_unzipped+'/glwd_3','-of','GTiff',processed_data_file]
completed_process = subprocess.run(cmd, shell=False)

'''
Upload processed data to Google Earth Engine
'''
# set up uploading chunk size
# The default setting requires an uploading speed at 10MB/min. Reduce the chunk size, if the network condition is not good.
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024* 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024* 1024  # 5 MB

logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storage
gcs_uris= util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcsBucket)  

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MODE' #check

# list the bands in each image
band_ids = ['b1']

# upload processed data file to GEE
# generate an asset name for the file by using the dataset name
asset_name = f'projects/resource-watch-gee/{dataset_name}'
# create the band manifest for this asset
mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': dataset_name+'_edit',
                 'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
# create complete manifest for asset upload
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
# copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    zipped.write(raw_data_file, os.path.basename(raw_data_file),compress_type= zipfile.ZIP_DEFLATED)

# upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    zipped.write(processed_data_file, os.path.basename(processed_data_file),compress_type= zipfile.ZIP_DEFLATED)

# upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))