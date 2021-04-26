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
import xarray
import rioxarray
import logging
import glob
import cdsapi


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
dataset_name = 'soc_068b_rw2_global_land_cover' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# download the data from the source
c = cdsapi.Client()
for year in range(1992,2020):
    if year<2016:
        c.retrieve(
            'satellite-land-cover',
            {
                'variable': 'all',
                'format': 'zip',
                'version': 'v2.0.7cds',
                'year': [
                    str(year)
                ],
            },
            os.path.join(data_dir,'data_'+str(year)+'.zip'))
    else:
        c.retrieve(
            'satellite-land-cover',
            {
                'variable': 'all',
                'format': 'zip',
                'version': 'v2.1.1',
                'year': [
                    str(year)
                ],
            },
            os.path.join(data_dir,'data_'+str(year)+'.zip'))

# unzip source data
raw_data_file = [os.path.join(data_dir,'data_'+str(year)+'.zip') for year in range(1992,2020)]
for raw_data in raw_data_file:
    zip_ref = ZipFile(raw_data, 'r')
    zip_ref.extractall(data_dir)
    zip_ref.close()
raw_data_file_unzipped = glob.glob(os.path.join(data_dir,'*.nc'))
raw_data_file_unzipped = sorted(raw_data_file_unzipped, key = lambda x: x.split('-')[7])

'''
Process data
'''
# convert the netcdf files to tif files
for raw_file in raw_data_file_unzipped:
    util_files.convert_netcdf(raw_file, ['lccs_class'])
processed_data_file = [os.path.join(raw_file[:-3]+'_lccs_class.tif') for raw_file in raw_data_file_unzipped]

'''
Upload processed data to Google Earth Engine
'''
# Set up uploading chunk size
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
for uri,year in zip(gcs_uris,range(1992,2020)):
    if 'ESACCI' in uri:
        # generate an asset name for the current file by using the filename (minus the file type extension)
        asset_name = f'projects/resource-watch-gee/{dataset_name}/{dataset_name}_{year}'
        # create the band manifest for this asset
        mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': os.path.basename(uri)[:-22],
                 'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
    else:
        # generate an asset name for the current file by using the filename (minus the file type extension)
        asset_name = f'projects/resource-watch-gee/{dataset_name}/{dataset_name}_{year}'
        # create the band manifest for this asset
        mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': os.path.basename(uri)[:-19],
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

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file),compress_type= zipfile.ZIP_DEFLATED)

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_file:
        zipped.write(file, os.path.basename(file),compress_type= zipfile.ZIP_DEFLATED)

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))