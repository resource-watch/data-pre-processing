import os
import boto3
from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import eeUtil
import subprocess

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
    INPUT   file: list of file names for netcdfs that we want to convert (stringKI)
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
# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check

# name bands according to variable names in original netcdf
bands = [{'id': var, 'tileset_band_index': vars.index(var), 'pyramiding_policy': pyramiding_policy} for var in vars]

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), key_data=os.getenv('GEE_JSON'))
ee.Initialize(auth)
eeUtil.init(service_account=os.getenv('GEE_SERVICE_ACCOUNT'), credential_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), project=os.getenv('CLOUDSDK_CORE_PROJECT'), bucket=os.getenv('GEE_STAGING_BUCKET'))

print('Uploading processed data to Google Earth Engine.')
# Upload processed data file to GEE
asset_name = f'/projects/resource-watch-gee/{dataset_name}'
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
