import os
import sys
if os.path.join(os.getenv('PROCESSING_DIR'), 'utils') not in sys.path:
    sys.path.append(os.path.join(os.getenv('PROCESSING_DIR'), 'utils'))
import util_files
import util_cloud
import urllib
from zipfile import ZipFile
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
dataset_name = 'ocn_008_historical_coral_bleaching_stress_frequency' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')

# insert the url used to download the data from the source website
url='ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/thermal_history/v2.1/noaa_crw_thermal_history_stress_freq_v2.1.nc'  #check

# download the data from the source
raw_data_file = os.path.join(data_dir,os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
# netcdf subdatasets that will be used in processing
subdatasets = ['n_gt0', # The number of events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
               'n_ge4', # The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
               'n_ge8', # The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
               'rp_gt0', # The average time between events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
               'rp_ge4', # The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
               'rp_ge8' # The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
              ]

logger.info('Extracting relevant GeoTIFFs from source NetCDF')
# convert netcdf to individual tif files for each of the subdatasets specified
tifs = util_files.convert_netcdf(raw_data_file, subdatasets)

# generate a name for processed tif
processed_data_file = os.path.join(data_dir, dataset_name+'.tif')

logger.info('Merge single-band GeoTIFFs into single, multiband GeoTIFF.')
# merge all the sub tifs from this netcdf to create an overall tif representing all variable
util_files.merge_geotiffs(tifs, processed_data_file)

'''
Upload processed data to Google Earth Engine
'''
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

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

# name bands according to variable names in original netcdf
bands = [{'id': var, 'tileset_band_index': subdatasets.index(var), 'tileset_id': dataset_name, 'pyramidingPolicy': pyramiding_policy} for var in subdatasets]

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
