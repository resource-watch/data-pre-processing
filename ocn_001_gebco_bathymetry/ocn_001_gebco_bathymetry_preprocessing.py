#Author: Kristine Lister
#Date: July 29th 2020
import os
import boto3
from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import eeUtil
from dotenv import load_dotenv
import shutil
import glob
import subprocess
import rasterio
load_dotenv(dotenv_path='/Users/kristine/WRI/cred/.env')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_001_gebco_bathymetry' #check

# first, set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/ocn_001_gebco_bathymetry'
path = os.path.join(os.getenv('PROCESSING_DIR'),dataset_name)
#move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
os.chdir(data_dir)

'''
Download data and save to your data directory

Bathymetry data can be downloaded by opening the following link in your browser. 
    
https://www.bodc.ac.uk/data/open_download/gebco/gebco_2020/geotiff/

This will download a file titled 'gebco_2020_geotiff.zip' to your Downloads folder. The zip file is about 3.7 GB in size (compressed).
    
Then uncompress the data file in your downloads folder which should create a folder 'gebco_2020_geotiff'
'''
download = os.path.join(os.path.expanduser("~"), 'Downloads', 'gebco_2020_geotiff')

# Move this file into your data directory
raw_data_folder = os.path.basename(download)
shutil.move(download,raw_data_folder)


'''
Process data
Merge separate geotiffs into one file
'''
#Create list of geotiffs in data folder
geotiffs = glob.glob(os.path.join(raw_data_folder,'*.tif'))

#Read no data value from geotiff
nodata_value = -32767 #this is the nodatavalue of the geotiffs, but it will be overwritten in the next two lines
with rasterio.open(geotiffs[0]) as src:
    nodata_value = src.nodatavals[0]

#Build virtual raster file to merge geotiffs
vrt_name = '{}.vrt'.format(dataset_name)
build_vrt_command = ('gdalbuildvrt {} {}').format(vrt_name, ' '.join(geotiffs))
print('Creating vrt file to merge geotiffs')
subprocess.check_output(build_vrt_command, shell=True)

#Merge geotiffs using gdal_translate, will create merged geotiff in data folder. This will take about five minutes.
geotiff_name = '{}_edit.tif'.format(dataset_name)
gdal_translate_command = ('gdal_translate {} {} -co COMPRESS=LZW -co BIGTIFF=YES').format(vrt_name, geotiff_name)
print('Merging geotiffs')
subprocess.check_output(gdal_translate_command, shell=True)


'''
Upload processed data to Google Earth Engine
'''
# initialize ee and eeUtil modules for uploading to Google Earth Engine
text_file = open("gcsPrivateKey.json", "w")
n = text_file.write(os.getenv('GEE_JSON'))
text_file.close()
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), key_data=os.getenv('GEE_JSON'))
ee.Initialize(auth)
eeUtil.init(service_account=os.getenv('GEE_SERVICE_ACCOUNT'), 
    credential_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), project=os.getenv('CLOUDSDK_CORE_PROJECT'), 
    bucket=os.getenv('GEE_STAGING_BUCKET'))

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# Set band value for b0
vars = ['b0']
bands = [{'id': var, 'tileset_band_index': vars.index(var), 'pyramiding_policy': pyramiding_policy, 'missing_data': {'values': [nodata_value]}} for var in vars]
processed_data_file = geotiff_name

print('Uploading processed data to Google Earth Engine.')
# Upload processed data file to GEE
asset_name = '/projects/resource-watch-gee/{}'.format(dataset_name)
eeUtil.uploadAsset(filename=processed_data_file, asset=asset_name, gs_prefix=dataset_name, public=True, bands=bands)
print('GEE asset created: {}'.format(asset_name))

# set dataset privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(asset_name[1:], acl)
print('Privacy set to public.')


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
# Copy the name of downloaded raw data to upload to S3
zip_download = os.path.join(os.path.expanduser("~"), 'Downloads', 'gebco_2020_geotiff.zip')
renamed_zip_download = os.path.join(os.path.expanduser("~"), 'Downloads', '{}.zip'.format(dataset_name))
rename_command = ('mv {} {}').format(zip_download, renamed_zip_download)
subprocess.check_output(rename_command, shell=True)
# Upload raw data file to S3
uploaded = upload_to_aws(renamed_zip_download, 'wri-projects', 'resourcewatch/raster/'+os.path.basename(renamed_zip_download))

print('Uploading processed data to S3.')
processed_data_dir = dataset_name + '_edit'
if not os.path.exists(processed_data_dir):
    os.mkdir(processed_data_dir)
shutil.move(processed_data_file,processed_data_dir)

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(processed_data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file)

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-projects', 'resourcewatch/raster/'+os.path.basename(processed_data_dir))
