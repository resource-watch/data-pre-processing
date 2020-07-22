import os
import boto3
from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import time
import glob

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'cli_030_aridity' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cli_030_aridity'
path = os.path.join(os.getenv('PROCESSING_DIR'),dataset_name)
#move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
    
'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'https://ndownloader.figshare.com/files/14118800' #check

# download the data from the source
raw_data_file = os.path.join(data_dir, 'global-ai_et0.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

# the path to the unprocessed data
raster = glob.glob(os.path.join(raw_data_file_unzipped, 'ai_et0', '*.tif'))[0]

# generate a name for processed tif 
processed_data_file = os.path.join(data_dir, dataset_name+'.tif')
# save the processed data
cmd = ['gdalwarp', raster, processed_data_file]
subprocess.call(cmd)

'''
Upload processed data to Google Earth Engine
'''
print('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gcsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcsBucket = gcsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

def gsStage(files, prefix=''):
    '''
    Upload files to Google Cloud Storage
    INPUT   files: location of file on local computer that you want to upload (string)
            prefix: optional, folder within GCS bucket where you want to upload the data (string)
    RETURN  gs_uris: list of uploaded data file locations on GCS (list of strings)
    '''
    # make sure the GCS bucket exists, create it if it does not
    if not gcsBucket.exists():
        print('Bucket {} does not exist, creating'.format(bucket))
        gcsBucket.create()
    # make sure files to be uploaded are formatted as a tuple
    files = (files,) if isinstance(files, str) else files
    # create an empty list to store the list of files we have uploaded to GCS
    gs_uris = []
    # loop through each file and upload
    for f in files:
        # define location within GCS bucket where the file should go
        path = '{}/{}'.format(prefix, os.path.basename(f))
        # format the full GCS path for the file
        uri = 'gs://{}/{}'.format(gcsBucket.name, path)
        print('Uploading {} to {}'.format(f, uri))
        # upload the file to GCS
        gcsBucket.blob(path).upload_from_filename(f)
        # add the file location to our list of uploaded files
        gs_uris.append(uri)
    return gs_uris

# upload local files to Google Cloud Storage
gs_uris = gsStage(processed_data_file, dataset_name)

print('Uploading processed data to Google Earth Engine.')

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

def ingestAsset(gs_uri, asset, date='', bands=[], public=False):
    '''
    Upload asset from Google Cloud Storage to Google Earth Engine
    INPUT   gs_uri: data file location on GCS, should be formatted `gs://<bucket>/<blob>` (string)
            asset: name of GEE asset destination path
            date: optional, date tag for asset (datetime.datetime or int ms since epoch)
            bands: optional, band name dictionary (list of dictionaries)
            public: do you want this asset to be public (Boolean)
    RETURN  task_id: Earth Engine task ID for file upload (string)
    '''
    # set up parameters for image task ingestion
    params = {'name': f'projects/earthengine-legacy/assets/{asset}',
              'tilesets': [{'id': os.path.basename(gs_uri).split('.')[0], 'sources': [{'uris': gs_uri}]}]}
    # if a date was input into the function, add it to the parameters
    if date:
        params['properties'] = {'time_start': formatDate(date),
                                'time_end': formatDate(date)}
    # if band parameters were included add them to the parameters
    if bands:
        if isinstance(bands[0], str):
            bands = [{'id': b} for b in bands]
        params['bands'] = bands
    # create a new task ID to ingest this asset
    task_id = ee.data.newTaskId()[0]
    print('Ingesting {} to {}: {}'.format(gs_uri, asset, task_id))
    # start ingestion process
    uploaded = False
    ee.data.startIngestion(task_id, params, True)
    # if process is still running, wait before checking ingestion again
    while uploaded == False:
        try:
            ee.data.getAsset(asset)
            uploaded = True
            print('GEE asset created: {}'.format(asset))
        except:
            time.sleep(60)
    if public==True:
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(asset, acl)
        print('Privacy set to public.')
    return task_id

task_id = ingestAsset(gs_uris[0], asset=asset_name, public=True)

def gsRemove(gs_uris):
    '''
    Delete files from Google Cloud Storage
    INPUT   gs_uris: list of data file locations on GCS that you want to delete (list of strings)
    '''
    # create a list of the files in Google Cloud Storage that should be deleted
    paths = []
    for path in gs_uris:
        paths.append(path[6 + len(gcsBucket.name):])
    # delete all files from Google Cloud Storage
    gcsBucket.delete_blobs(paths, lambda x:x)

gsRemove(gs_uris)

print('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        print("http://{}.s3.amazonaws.com/{}".format(bucket, s3_file))
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

print('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))