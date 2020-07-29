import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
import xarray
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
dataset_name = 'cit_031_air_quality_PM25_concentration' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)
    
'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
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
    Since the latitude and longitude of this netcdf are reversed, this function first transposes
    the 'LAT' and 'LON' dimensions of the netcdf file before exporting it as a GeoTIFF
    INPUT   file: file name for netcdf that we want to convert (string)
            outfile_name: file name for tif we will generate (string)
    '''
    # open netcdf file
    xds = xarray.open_dataset(input_file)
    # transpose 'LAT' and 'LON' dimensions because they were reversed
    PM25 = xds.PM25.transpose('LAT', 'LON')
    # define the name of the variables to be used for the x and y dimensions in the dataset
    PM25.rio.set_spatial_dims(x_dim="LON", y_dim="LAT", inplace=True)
    # add crs information to data
    PM25.rio.write_crs("EPSG:4326", inplace=True)
    # translate the netcdf file into a tif
    PM25.rio.to_raster(output_file[:-4] + '_pre.tif')
    
    # reexport the tif using gdalwarp to fix the origin issue
    cmd = ['gdalwarp', output_file[:-4] + '_pre.tif', output_file]
    subprocess.call(cmd)

# create a list containing the paths to the processed files 
processed_data_file = []
for url in url_list:
    # find the index in the filename string where the underscore before the year begins
    year_loc = os.path.basename(url).index('_20')
    # generate a name for the processed data file by joining the dataset name with an underscore and the year of data
    processed_file_name = dataset_name + os.path.basename(url)[year_loc: year_loc + 5] + '.tif'
    # add the full processed data file location to the list of processed data file locations
    processed_data_file.append(os.path.join(data_dir, processed_file_name))

logger.info('Extracting relevant GeoTIFFs from source NetCDF')
# convert the netcdf files to tif files
for raw_file, processed_file in zip(raw_data_file, processed_data_file):
    convert(raw_file, processed_file)
    logger.info(processed_file + ' created')
    
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

# Create an image collection where we will put the processed data files in GEE
image_collection = f'projects/resource-watch-gee/{dataset_name}'
ee.data.createAsset({'type': 'ImageCollection'}, image_collection)

# set image collection's privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(image_collection, acl)
print('Privacy set to public.')

# list the bands in each image
band_ids = ['PM25']

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
# Upload raw data file to S3

print('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_file:
        zipped.write(file, os.path.basename(file))

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
