import os
import urllib.request
from urllib.parse import urlsplit
import re
import sys
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import util_cloud
import logging
import subprocess
from google.cloud import storage
import ee
import zipfile
from zipfile import ZipFile
import fnmatch

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
dataset_name = 'foo_067_rw0_crop_suitability_class'

logger.info('Executing script for dataset: ' + dataset_name)

'''
Download data and save to your data directory
'''
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# create a list of rice ensemble tifs
# note: these were created from the rice_ensemble_processing.py script and there should be a total of 12 files
raw_rice_ensemble_file = []
# list contents of data directory and use fnmatch to find rice ensemble files
files_list = os.listdir(data_dir)
for file in files_list:
    if fnmatch.fnmatch(file, 'ENSEMBLE_*_rc*.tif'):
        raw_rice_ensemble_file.append(os.path.join(data_dir, file))

# list of urls from data source
# urls downloaded from GAEZv4 data portal: https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer
# under Theme 4: Suitability and Attainable Yield
# sub-theme: Suitability Index / Variable name: Suitability index range (0-10000); current cropland in grid cell
url_list = [
        # cotton tifs
            # irrigation
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHi_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2020sH/suHi_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2020sH/suHi_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2050sH/suHi_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2050sH/suHi_cot.tif',
            # rainfed
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHr_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2020sH/suHr_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2020sH/suHr_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2050sH/suHr_cot.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2050sH/suHr_cot.tif',
        # coffee tifs
            # irrigation
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHi_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2020sH/suHi_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2020sH/suHi_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2050sH/suHi_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2050sH/suHi_cof.tif',
            # rainfed
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHr_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2020sH/suHr_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2020sH/suHr_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp4p5/2050sH/suHr_cof.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/ENSEMBLE/rcp8p5/2050sH/suHr_cof.tif',
        # rice tifs
            # NOTE - these are historical tifs for wetland/dryland rice only; have to manually compute ENSEMBLEs (see rice_ensemble_processing.py)
            # wetland rice - gravity irrigation
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHg_rcw.tif',
            # wetland rice - rainfed
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHr_rcw.tif',
            # dryland rice - rainfed
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/CRUTS32/Hist/8110H/suHr_rcd.tif'
        ]

# download tifs and rename as they are downloaded because some have the same name when downloaded
# files are renamed based on their unique path information that is contained in the urls
raw_data_file = []
for url in url_list:
    # split URL to access path info
    s = urlsplit(url)
    # swap "/" for "-" in the path
    r = re.sub("/", "-", s.path)
    # remove the beginning portion of path which is common to all urls
    p = r.replace("-data.gaezdev.aws.fao.org-res05-", "")
    # create a new path and filename
    filename = os.path.join(data_dir, p)
    # download data and save with new filename in data_dir
    d = urllib.request.urlretrieve(url, filename)
    raw_data_file.append(d[0])

# add rice ensembles to list of raw data files
for rr in raw_rice_ensemble_file:
    raw_data_file.append(rr)

'''
Process data
'''
# generate names for processed tif files
processed_data_file = [x[:-4]+'_edit'+x[-4:] for x in raw_data_file]

# rename the tif file and process with gdal
for raw, processed in zip(raw_data_file, processed_data_file):
    # set nodata to -9 (as defined by source in tif)
    cmd = 'gdalwarp -dstnodata -9 {} {}'.format(raw, processed)
    subprocess.check_output(cmd, shell=True)

'''
Upload processed data to Google Earth Engine
'''
# set up uploading chunk size
# the default setting requires an uploading speed at 10MB/min. Reduce the chunk size, if the network condition is not good.
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
pyramiding_policy = 'MEAN' #check

# create an image collection where we will put the processed data files in GEE
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
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_file:
        zipped.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))

