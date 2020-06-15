import os
import boto3
from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import time

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_008_historic_coral_bleaching_stress_frequency' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ene_034_electricity_consumption'
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
url='ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/thermal_history/v2.1/noaa_crw_thermal_history_stress_freq_v2.1.nc'  #check

# download the data from the source
raw_data_file = os.path.join(data_dir,os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

'''
Process data
'''
def convert(file, vars, outfile_name):
    '''
    Convert netcdf files to tifs
    INPUT   file: list of file names for netcdfs that we want to convert (string)
            vars: list of variables we want to pull from the source dataset (list of strings)
    RETURN  tifs: list of file names for tifs that have been generated (list of strings)
    '''
    # create an empty list to store the names of the tifs we generate from this netcdf file
    band_tifs = []
    # go through each variables to process in this netcdf file
    for var in vars:
        # extract subdataset by name
        # should be of the format 'NETCDF:"filename.nc":variable'
        sds_path = f'NETCDF:"{file}":{var}'
        # generate a name to save the tif file we will translate the netcdf file's subdataset into
        band_tif = '{}_{}.tif'.format(os.path.splitext(file)[0], sds_path.split(':')[-1])
        # translate the netcdf file's subdataset into a tif
        cmd = ['gdal_translate','-q', '-a_srs', 'EPSG:4326', sds_path, band_tif]
        subprocess.call(cmd)
        # add the new subdataset tif files to the list of tifs generated from this netcdf file
        band_tifs.append(band_tif)
    # merge all the sub tifs from this netcdf to create an overall tif representing all variable
    merge_cmd = ['gdal_merge.py', '-separate'] + band_tifs + ['-o', outfile_name]
    separator = " "
    merge_cmd = separator.join(merge_cmd)
    subprocess.call(merge_cmd, shell=True)

# variables in netcdf to be converted to tifs
vars = ['n_gt0', # The number of events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
        'n_ge4', # The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
        'n_ge8', # The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
        'rp_gt0', # The average time between events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
        'rp_ge4', # The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
        'rp_ge8' # The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
        ]

# generate a name for processed tif
processed_data_file = os.path.join(data_dir, dataset_name+'.tif')

# convert the listed variables into tif files then merge them into a single tif file with a band for each variable
convert(raw_data_file, vars, processed_data_file)

'''
Upload processed data to Google Earth Engine
'''
print('Uploading processed data to Google Cloud Storage.')
# set up Google Cloud Storage project and bucket objects
gsClient = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gsBucket = gsClient.bucket(os.environ.get("GEE_STAGING_BUCKET"))

def gsStage(files, prefix=''):
    '''
    Upload files to Google Cloud Storage
    INPUT   files: location of file on local computer that you want to upload (string)
            prefix: optional, folder within GCS bucket where you want to upload the data (string)
    RETURN  gs_uris: list of uploaded data file locations on GCS (list of strings)
    '''
    # make sure the GCS bucket exists, create it if it does not
    if not gsBucket.exists():
        print('Bucket {} does not exist, creating'.format(bucket))
        gsBucket.create()
    # make sure files to be uploaded are formatted as a tuple
    files = (files,) if isinstance(files, str) else files
    # create an empty list to store the list of files we have uploaded to GCS
    gs_uris = []
    # loop through each file and upload
    for f in files:
        # define location within GCS bucket where the file should go
        path = '{}/{}'.format(prefix, os.path.basename(f))
        # format the full GCS path for the file
        uri = 'gs://{}/{}'.format(gsBucket.name, path)
        print('Uploading {} to {}'.format(f, uri))
        # upload the file to GCS
        gsBucket.blob(path).upload_from_filename(f)
        # add the file location to our list of uploaded files
        gs_uris.append(uri)
    return gs_uris

# upload local files to Google Cloud Storage
gs_uris = gsStage(processed_data_file, dataset_name)

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

print('Uploading processed data to Google Earth Engine.')

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# name bands according to variable names in original netcdf
bands = [{'id': var, 'tileset_band_index': vars.index(var), 'tileset_id': dataset_name, 'pyramidingPolicy': pyramiding_policy} for var in vars]

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

def ingestAssets(gs_uri, asset, date='', bands=[], public=False):
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
    ee.data.startIngestion(task_id, params, True)
    # if process is still running, wait before checking ingestion again
    status = ee.data.getTaskStatus(task_id)[0]['state']
    while status=='RUNNING':
        time.sleep(30)
        status = ee.data.getTaskStatus(task_id)[0]['state']
    print(status)
    if public==True:
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(asset_name, acl)
        print('Privacy set to public.')
    return task_id

task_id = ingestAsset(gs_uris[0], asset=asset_name, bands=bands, public=True)
print('GEE asset created: {}'.format(asset_name))


def gsRemove(gs_uris):
    '''
    Delete files from Google Cloud Storage
    INPUT   gs_uris: list of data file locations on GCS that you want to delete (list of strings)
    '''
    # create a list of the files in Google Cloud Storage that should be deleted
    paths = []
    for path in gs_uris:
        paths.append(path[6 + len(gsBucket.name):])
    # delete all files from Google Cloud Storage
    gsBucket.delete_blobs(paths, lambda x:x)

gsRemove(gs_uris)
print('Files deleted from Google Cloud Storage.')

'''
Upload original data and processed data to Amazon S3 storage
'''
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
uploaded = upload_to_aws(raw_data_dir, 'wri-projects', 'resourcewatch/raster/'+os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-projects', 'resourcewatch/raster/'+os.path.basename(processed_data_dir))
