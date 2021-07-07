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

# create a dictionary to store information about the dataset
data_dict = OrderedDict()

data_dict= {
    'url': None,
    'tifs': ['global_Erosion_2002.tif', 'global_Erosion_2007.tif', 'global_Erosion_2012.tif', 'global_Erosion_2017.tif','global_Erosion_2020.tif'],
    'raw_data_file':[],
    'processed_data_file': [],
    'sds': [
        'classification',
    ],
    'missing_data': [65533,
    ],
    'pyramiding_policy': 'MEAN',
    'band_ids': []
}

'''
Download the data and move to your data directory 
The data was provided directly from the source as a GeoTiff and downloaded manually into the downloads folder. 
For access to the most recent data, please contact the principal author Tor Vagen (t.vagen@cgiar.org).access to the most recent data, please contact the principal author Tor Vagen (t.vagen@cgiar.org).
'''

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
for i in range(len(data_dict['tifs'])):
    # set a new file name to represent processed data
    year= data_dict['tifs'][i][15:19]
    data_dict['processed_data_file'].append(os.path.join(data_dir,dataset_name + '_' + year +'.tif'))

    logger.info('Processing data for ' + data_dict['processed_data_file'][i])
    # project the data into into WGS84 (espg 4326) using the command line terminal
    cmd = 'gdalwarp -of GTiff -t_srs EPSG:4326 {} {}'
    # format to command line
    posix_cmd = shlex.split(cmd.format(data_dict['raw_data_file'][i], data_dict['processed_data_file'][i]), posix=True)     
    completed_process= subprocess.check_call(posix_cmd)   
    logging.debug(str(completed_process))

'''
Upload processed data to Google Earth Engine
'''

# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

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
band_ids = ['classification']

task_id = []


# Upload processed data files to GEE

# if upload is timing out, uncomment the following lines
# storage.blob._DEFAULT_CHUNKSIZE = 10 * 1024* 1024  # 10 MB
# storage.blob._MAX_MULTIPART_SIZE = 10 * 1024* 1024  # 10 MB

#loop though the processed data files to upload to Google Cloud Storage and Google Earth Engine
for i in range(len(data_dict['tifs'])):
    logger.info('Uploading '+ data_dict['processed_data_file'][i]+' to Google Cloud Storage.')
    # upload files to Google Cloud Storage
    gcs_uri= util_cloud.gcs_upload(data_dict['raw_data_file'][i], dataset_name, gcs_bucket=gcsBucket)
    
    logger.info('Uploading '+ data_dict['processed_data_file'][i]+ 'Google Earth Engine.')
    # generate an asset name for the current file by using the filename (minus the file type extension)
    file_name=data_dict['processed_data_file'][i].split('.')[0].split('/')[1]
    asset_name = f'projects/resource-watch-gee/{dataset_name}/{file_name}'
    
    # create the band manifest for this asset
    tileset_id= data_dict['tifs'][i].split('.')[0]
    missing_values = [65533, 
            ]
    mf_bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'missing_data': {'values': missing_values}, 'tileset_id': tileset_id,'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]
    
    # create complete manifest for asset upload
    manifest = util_cloud.gee_manifest_complete(asset_name, gcs_uri[0], mf_bands)
    
    # upload the file from GCS to GEE
    task = util_cloud.gee_ingest(manifest)
    print(asset_name + ' uploaded to GEE')
    task_id.append(task)
    
    # remove files from Google Cloud Storage
    util_cloud.gcs_remove(gcs_uri, gcs_bucket=gcsBucket)
    logger.info('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

# Copy the raw data into a zipped file to upload to S3

print('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
     raw_data_files = data_dict['raw_data_file']
     for raw_data_file in raw_data_files:
        zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    processed_data_files = data_dict['processed_data_file']
    for procedded_data_file in processed_data_files:
        zip.write(procedded_data_file, os.path.basename(raw_data_file))

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
