import os
import sys
import dotenv
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import subprocess
import shutil
from zipfile import ZipFile
import ee
from google.cloud import storage
import logging  
import re
import glob
from collections import OrderedDict  
import shlex

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
dataset_name = 'wat_070_rw0_soil_erosion'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
The data was provided directly from the source as a GeoTiff. For access to the most recent data, 
please contact the principal author Tor Vagen (t.vagen@cgiar.org).

Download data to your Downloads folder.
'''
data_dict = OrderedDict()

data_dict= {
    'url': None,
    'tifs': ['global_Erosion_2002.tif', 'global_Erosion_2007.tif', 'global_Erosion_2012.tif','global_Erosion_2017.tif','global_Erosion_2020.tif'],
    'raw_data_file':[],
    'processed_data_file': [],
    'sds': [
        'classification',
    ],
    'missing_data': [
        -9999.000, 65533,
    ],
    'pyramiding_policy': 'MEAN',
    'band_ids': []
}


# move the data from 'Downloads' into the data directory
for tif in data_dict['tifs']:
    source_dir = os.path.join(os.getenv("DOWNLOAD_DIR"), tif)
    dest_dir = os.path.abspath(data_dir)
    shutil.copy(source_dir, dest_dir)

    # set name of raw data files
    data_dict['raw_data_file'].append(os.path.join(data_dir,tif))

'''
Process data
'''
# Create file name for processed data
# for i in range(len(data_dict['tifs'])):
#     year= data_dict['tifs'][i][15:19]
#     data_dict['processed_data_file'].append(os.path.join(data_dir,dataset_name + '_' + year +'.tif'))

#     logger.info(data_dict['processed_data_file'][i])

   
#     cmd = 'gdalwarp -of GTiff -t_srs EPSG:4326 {} {}'
#     # format to command line
#     posix_cmd = shlex.split(cmd.format(data_dict['raw_data_file'][i], data_dict['processed_data_file'][i]), posix=True)     
#     #completed_process= subprocess.check_call(posix_cmd)   
#     #logging.debug(str(completed_process))

processed_data_file= os.path.join(data_dir,dataset_name +'.tif')


cmd= 'gdalbuildvrt -separate data/stack.vrt ' + ' '.join(data_dict['raw_data_file'])
posix_cmd = shlex.split(cmd)
# completed_process= subprocess.check_call(posix_cmd)   
# logging.debug(str(completed_process))

cmd= 'gdal_translate data/stack.vrt' + processed_data_file 
posix_cmd = shlex.split(cmd)
# completed_process= subprocess.check_call(posix_cmd)   
# logging.debug(str(completed_process))

# '''
# Upload processed data to Google Earth Engine
# '''

# The default setting requires an uploading speed at 10MB/min. Reduce the chunk size, if the network condition is not good.
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024* 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024* 1024  # 5 MB

logger.info('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# upload files to Google Cloud Storage
gcs_uris = ['gs://rw-nrt/wat_070_rw0_soil_erosion/wat_070_rw0_soil_erosion.tif'] #util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcsBucket )
print(gcs_uris)

logger.info('Uploading processed data to Google Earth Engine.')
# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

# name bands according to variable names in original tif
band_ids = ['b1', 'b2', 'b3', 'b4', 'b5'
           ]
 
# list missing values in the original tif 
missing_values = [65533, 
            ]
mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'missing_data': {'values': missing_values}, 'tileset_id': dataset_name,
             'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
# create manifest for asset upload
manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uris[0], mf_bands)
# upload processed data file to GEE
task_id = util_cloud.gee_ingest(manifest, public=True)
# remove files from Google Cloud Storage
# util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcsBucket)
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
    for file in data_dict['raw_data_file']:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
#Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))


