# Author: Peter Kerins  
# Date: 2020 Jun 23
import os
import sys
import dotenv
dotenv.load_dotenv(os.path.abspath(os.getenv('RW_ENV')))

utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
from zipfile import ZipFile
import ee
from google.cloud import storage
from shutil import copyfile

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
dataset_name = 'ocn_005_historical_cyclone_intensity'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# data source page:
#     https://preview.grid.unep.ch/index.php?preview=data&events=cyclones&evcat=4&lang=eng
# access dataset via "DOWNLOAD" option in sidebar, which prompts javascript popup
# download data as GeoTiff
# place resulting zip file in data folder
# expected file name as of june 2020: 
#     cy_intensity_20200408183708_tiff.zip

# set name of raw data file
raw_data_file = os.path.join(data_dir,'cy_intensity_20200408183708_tiff.zip')

logger.info('Unzip raw data')
with ZipFile(raw_data_file, 'r') as zip:
    namelist = zip.namelist()
    tifnames = [name for name in namelist if '.tif' in name]
    if len(tifnames) != 1:
        raise Exception()
    tifname = tifnames[0]
    zip.extractall(data_dir)

'''
Process data
'''
# in this case "processed" data file is just unzipped tif
# but we have to rename it
unprocessed_data_file = (os.path.join(data_dir,tifname))
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')
logger.info(processed_data_file)
copyfile(unprocessed_data_file, processed_data_file)

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

# name bands according to variable names in original netcdf
band_ids = ['cy_intensity',
           ]

mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': dataset_name,
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
