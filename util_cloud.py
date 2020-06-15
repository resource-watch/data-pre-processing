import os
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))
import boto3
from botocore.exceptions import NoCredentialsError
import time
import ee
from google.cloud import storage

def gcs_upload(files, prefix='', gcs_bucket=None):
    '''
    Upload files to Google Cloud Storage
    INPUT   files: location of file on local computer that you want to upload (string)
            prefix: optional, folder within GCS bucket where you want to upload the data (string)
    RETURN  gcs_uris: list of uploaded data file locations on GCS (list of strings)
    '''
    # make sure the GCS bucket exists, create it if it does not
    if gcs_bucket is None:
        print('No bucket passed, creating {}'.format(os.environ.get("GEE_STAGING_BUCKET")))
        gcs_bucket = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT")).bucket(os.environ.get("GEE_STAGING_BUCKET"))
    elif not gcs_bucket.exists():
        print('Bucket {} does not exist, creating'.format(os.environ.get("GEE_STAGING_BUCKET")))
        gcs_bucket.create()
    # make sure files to be uploaded are formatted as a tuple
    files = (files,) if isinstance(files, str) else files
    # create an empty list to store the list of files we have uploaded to GCS
    gcs_uris = []
    # loop through each file and upload
    for f in files:
        # define location within GCS bucket where the file should go
        path = '{}/{}'.format(prefix, os.path.basename(f))
        # format the full GCS path for the file
        uri = 'gs://{}/{}'.format(gcs_bucket.name, path)
        print('Uploading {} to {}'.format(f, uri))
        # upload the file to GCS
        gcs_bucket.blob(path).upload_from_filename(f)
        # add the file location to our list of uploaded files
        gcs_uris.append(uri)
    return gcs_uris

def gee_ingest(gcs_uri, asset, date='', bands=[], public=False):
    '''
    Upload asset from Google Cloud Storage to Google Earth Engine
    INPUT   gcs_uri: data file location on GCS, should be formatted `gs://<bucket>/<blob>` (string)
            asset: name of GEE asset destination path
            date: optional, date tag for asset (datetime.datetime or int ms since epoch)
            bands: optional, band name dictionary (list of dictionaries)
            public: do you want this asset to be public (Boolean)
    RETURN  task_id: Earth Engine task ID for file upload (string)
    '''
    # set up parameters for image task ingestion
    params = {'name': f'projects/earthengine-legacy/assets/{asset}',
              'tilesets': [{'id': os.path.basename(gcs_uri).split('.')[0], 'sources': [{'uris': gcs_uri}]}]}
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
    print('Ingesting {} to {}: {}'.format(gcs_uri, asset, task_id))
    # start ingestion process
    uploaded = False
    print(gcs_uri)
    print(params)
    ee.data.startIngestion(task_id, params, True)
    # if process is still running, wait before checking ingestion again
    while uploaded == False:
        try:
            ee.data.getAsset(asset)
            uploaded = True
            print('GEE asset created: {}'.format(asset))
        except:
            time.sleep(30)
    if public==True:
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(asset, acl)
        print('Privacy set to public.')
    return task_id

def gcs_remove(gcs_uris, gcs_bucket=None):
    '''
    Delete files from Google Cloud Storage
    INPUT   gcs_uris: list of data file locations on GCS that you want to delete (list of strings)
    '''
    # make sure the GCS bucket exists, create it if it does not
    if gcs_bucket is None:
        print('No bucket passed, creating {}'.format(os.environ.get("GEE_STAGING_BUCKET")))
        gcs_bucket = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT")).bucket(os.environ.get("GEE_STAGING_BUCKET"))
    elif not gcs_bucket.exists():
        print('Bucket {} does not exist, creating'.format(os.environ.get("GEE_STAGING_BUCKET")))
        gcs_bucket.create()
    # create a list of the files in Google Cloud Storage that should be deleted
    paths = []
    for path in gcs_uris:
        paths.append(path[6 + len(gcs_bucket.name):])
    # delete all files from Google Cloud Storage
    gcs_bucket.delete_blobs(paths, lambda x:x)
    
def aws_upload(local_file, bucket, s3_file):
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