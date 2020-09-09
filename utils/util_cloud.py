import os
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))
import boto3
from botocore.exceptions import NoCredentialsError
import time
import ee
from google.cloud import storage
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def gcs_upload(files, prefix='', gcs_bucket=None):
    '''
    Upload files to Google Cloud Storage
    INPUT   files: location of file on local computer that you want to upload (string)
            prefix: optional, folder within GCS bucket where you want to upload the data (string)
    RETURN  gcs_uris: list of uploaded data file locations on GCS (list of strings)
    '''
    # make sure the GCS bucket exists, create it if it does not
    if gcs_bucket is None:
        logger.debug('No bucket passed, creating {}'.format(os.environ.get("GEE_STAGING_BUCKET")))
        gcs_bucket = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT")).bucket(os.environ.get("GEE_STAGING_BUCKET"))
    elif not gcs_bucket.exists():
        logger.debug('Bucket {} does not exist, creating'.format(os.environ.get("GEE_STAGING_BUCKET")))
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
        logger.debug('Uploading {} to {}'.format(f, uri))
        # upload the file to GCS
        blob = gcs_bucket.blob(path)
        blob._chunk_size = 5 * 1024* 1024
        blob.upload_from_filename(f)
        # add the file location to our list of uploaded files
        gcs_uris.append(uri)
    return gcs_uris

def millis_since_epoch(date):
    '''
    Format date as milliseconds since last epoch
    INPUT   date: datetime to be converted (datetime)
    RETURN date in milliseconds since last epoch (integer)
    '''
    if isinstance(date, int):
        return date
    seconds = (date - datetime.datetime.utcfromtimestamp(0)).total_seconds()
    return int(seconds * 1000)
    
def gee_manifest_bands(bands_dict, dataset_name):
    '''
    Create bands manifest for image upload to GEE (https://developers.google.com/earth-engine/image_manifest)
    INPUT   bands_dict: dictionary in which keys are band names and values are dictionaries containing a list of no-data values and the pyramiding policy to use in Google Earth Engine (dictionary)
            dataset_name: name of the asset being uploaded to GEE (string)
    RETURN  bands_mf: band manifest for asset upload into GEE, in the form of a list of dictionaries, with each dictionary containing parameters for an image band (list of dictionaries)
    '''
    bands_mf = []
    i = 0
    for key, val in bands_dict.items():
        if 'band_ids' not in val:
            mf_element = {
                'id': key,
                'tileset_band_index': i,
                'tileset_id': dataset_name,
                'missing_data': {
                    'values': val['missing_data'],
                },
                'pyramiding_policy': val['pyramiding_policy'],
            }
            i += 1
            bands_mf.append(mf_element)
        else:
            for band_id in val['band_ids']:
                mf_element = {
                    'id': band_id,
                    'tileset_band_index': i,
                    'tileset_id': dataset_name,
                    'missing_data': {
                        'values': val['missing_data'],
                    },
                    'pyramiding_policy': val['pyramiding_policy'],
                }
                i += 1
                bands_mf.append(mf_element)            
    return bands_mf

def gee_manifest_complete(asset, gcs_uri, mf_bands, date=''):
    '''
    Create complete manifest for image upload to GEE (https://developers.google.com/earth-engine/image_manifest)
    INPUT   asset: name of the asset being uploaded to GEE (string)
            gs_uri: data file location on GCS, should be formatted `gs://<bucket>/<blob>` (string)
            mf_bands: band manifest, created with gee_manifest_bands function (dictionary)
            date: optional, date tag for asset (datetime.datetime or int ms since epoch)
    RETURN  manifest: complete manifest for asset upload into GEE (dictionary)
    '''
    # set up parameters for image task ingestion
    manifest = {'name': f'projects/earthengine-legacy/assets/{asset}',
              'tilesets': [{'id': os.path.basename(gcs_uri).split('.')[0], 'sources': [{'uris': gcs_uri}]}]}
    # if a date was input into the function, add it to the parameters
    if date:
        manifest['properties'] = {'time_start': millis_since_epoch(date),
                                'time_end': millis_since_epoch(date)}
    manifest['bands'] = mf_bands
    return manifest

def gee_ingest(manifest, public=False):
    '''
    Upload asset from Google Cloud Storage to Google Earth Engine
    INPUT   manifest: image manifest, specifying how asset should be ingested into GEE (dictionary)
            public: whether the asset should be publicly available on GEE (boolean)
    RETURN  task_id: Earth Engine task ID for file upload (string)
    '''
    # create a new task ID to ingest this asset
    task_id = ee.data.newTaskId()[0]
    # start ingestion process
    uploaded = False
    logger.debug('Submitting asset for upload to GEE using the following manifest: \n' + str(manifest))
    ee.data.startIngestion(task_id, manifest, True)
    # if process is still running, wait before checking ingestion again
    while uploaded == False:
        try:
            ee.data.getAsset(manifest['name'])
            uploaded = True
            logger.debug('GEE asset created: {}'.format(asset))
        except:
            time.sleep(30)
    if public==True:
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(manifest['name'], acl)
        logger.debug('Privacy set to public.')
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
    '''
    Upload original data and processed data to Amazon S3 storage
    INPUT   local_file: local file to be uploaded to AWS (string)
        bucket: AWS bucket where file should be uploaded (string)
        s3_file: path where file should be uploaded within the input AWS bucket (string)
    '''
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'))
    try:
        s3.upload_file(local_file, bucket, s3_file)
        logger.info("AWS upload successful: http://{}.s3.amazonaws.com/{}".format(bucket, s3_file))
        return True
    except FileNotFoundError:
        logger.error("aws_upload - file was not found: + local_file.")
        return False
    except NoCredentialsError:
        logger.error("aws_upload - credentials not available.")
        return False
