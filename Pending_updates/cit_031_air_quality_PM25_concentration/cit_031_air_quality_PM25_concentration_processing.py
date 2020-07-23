import os
import boto3
from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import time
import rasterio as rio
import numpy as np
import xarray
import rioxarray

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'cit_031_air_quality_PM25_concentration' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cit_031_air_quality_PM25_concentration'
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
url_list = ['http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201101_201112_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201201_201212_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201301_201312_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201401_201412_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201501_201512_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201601_201612_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201701_201712_0p01.nc',
            'http://fizz.phys.dal.ca/~atmos/datasets/EST2020/ACAG_PM25_GWR_V4GL03_201801_201812_0p01.nc']

# download the data from the source
raw_data_file = [os.path.join(data_dir,os.path.basename(url)) for url in url_list]
for url, file in zip(url_list, raw_data_file):
     urllib.request.urlretrieve(url, file)

'''
Process data
'''
def convert(input_file, output_file):
    '''
    Convert netcdf files to tifs
    INPUT   file: file name for netcdf that we want to convert (string)
            outfile_name: file name for tif we will generate (string)
    '''
    # translate the netcdf file into a tif
    xds = xarray.open_dataset(input_file)
    PM25 = xds.PM25.transpose('LAT', 'LON')
    PM25.rio.set_spatial_dims(x_dim="LON", y_dim="LAT", inplace=True)
    PM25.rio.write_crs("EPSG:4326", inplace=True)
    PM25.rio.to_raster(output_file[:-4] + '_pre.tif')
    
    # reexport the tif using gdalwarp to fix the origin issue
    cmd = ['gdalwarp', output_file[:-4] + '_pre.tif', output_file]
    subprocess.call(cmd)

# create a list containing the paths to the processed files 
processed_data_file = []
for url in url_list:
    year_loc = os.path.basename(url).index('_20')
    processed_file_name = dataset_name + os.path.basename(url)[year_loc: year_loc + 5] + '.tif'
    processed_data_file.append(os.path.join(data_dir, processed_file_name))

# convert the netcdf files to tif files
for raw_file, processed_file in zip(raw_data_file, processed_data_file):
    convert(raw_file, processed_file)
    print(processed_file + ' created')
    
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

# Upload processed data file to GEE
image_collection = f'projects/resource-watch-gee/{dataset_name}'
ee.data.createAsset({'type': 'ImageCollection'}, image_collection)

# set dataset privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(image_collection, acl)
print('Privacy set to public.')

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

task_id = []
for uri in gs_uris:
    asset_name = f'projects/resource-watch-gee/{dataset_name}/{os.path.basename(uri)[:-4]}'
    task = ingestAsset(uri, asset=asset_name)
    print(asset_name + ' uploaded to GEE')
    task_id.append(task)

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
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, 'wri-projects', 'resourcewatch/raster/'+ os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_file:
        zipped.write(file, os.path.basename(file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-projects', 'resourcewatch/raster/'+ os.path.basename(processed_data_dir))
