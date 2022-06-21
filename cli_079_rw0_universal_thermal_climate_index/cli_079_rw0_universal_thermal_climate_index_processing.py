import os
import sys
import cdsapi
from zipfile import ZipFile
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import util_cloud
import netCDF4
import numpy as np
import rasterio
from rasterio.crs import CRS
import fnmatch
import logging
import ee
from google.cloud import storage
import zipfile


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
dataset_name = 'cli_079_rw0_universal_thermal_climate_index'

logger.info('Executing script for dataset: ' + dataset_name)

'''
Download data
'''
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# declare years and months to download data for
# NOTE: data is large -- files for 2021 + 2022 are 13G total and takes awhile to download ( on the order of a couple of hours for everything)
# years list = '2021' and '2022'
years = ['2022']
# 2021 months list = ['05', '06', '07', '08', '09', '10', '11', '12']
# 2022 months list = ['01', '02', '03', '04']
months = ['01', '02', '03', '04']

# access CDS API to download UTCI data; for more info see: https://cds.climate.copernicus.eu/api-how-to
c = cdsapi.Client()
c.retrieve(
    'derived-utci-historical',
    {
        'variable': 'universal_thermal_climate_index',
        'version': '1_1',
        'product_type': 'consolidated_dataset',
        'year': [
            *years,
        ],
        'month': [
            *months,
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'format': 'zip',
    },
    os.path.join(data_dir, 'utci_download.zip'))

# unzip source data
with ZipFile('data/utci_download.zip', 'r') as zip_obj:
    # create list of raw file names
    raw_file = zip_obj.namelist()
    zip_obj.extractall(data_dir)
    zip_obj.close()

logger.info('Finished downloading data from CDS')

# create a list of paths for the netcdf files
raw_file = [os.path.abspath(os.path.join(data_dir, p)) for p in raw_file]

# remove dots from filenames and replace with underscores
for rf in raw_file:
    # split path into root and extension
    p = os.path.splitext(rf)
    # isolate the root
    name = p[0]
    # replace the dots with underscores
    nodots = name.replace('.', '_')
    new_name = nodots+p[1]
    # rename files
    os.rename(rf, new_name)

# create a list of raw data file names
raw_data_file = [os.path.abspath(os.path.join(data_dir, file)) for file in os.listdir(data_dir) if file.endswith('.nc')]

'''
Process Data
'''
# open netcdf files and calculate daily mean
daily_mean_tifs = []
for file in raw_data_file:
    raw_data = netCDF4.Dataset(file, 'r')
    # isolate the universal thermal climate index (utci) variable
    raw_utci = raw_data.variables['utci'][:]
    # convert from kelvin to celsius (subtract 273.15)
    utci_degc = np.subtract(raw_utci, 273.15)
    # get daily average, use numpy mean to get the average value across the 24 hours (bands)
    daily_utci_degc = np.mean(utci_degc, axis=0)
    # save daily average to a new tif file, all metadata can be found from viewing the raw_data variable
    with rasterio.open(os.path.join(data_dir, os.path.splitext(file)[0]+'_daily_edit.tif'),
                       'w',
                       driver='GTiff',
                       height=daily_utci_degc.shape[0],
                       width=daily_utci_degc.shape[1],
                       count=1,
                       dtype=daily_utci_degc.dtype,
                       nodata=-9.0e33,
                       crs=CRS.from_epsg(4326),
                       transform=(0.25, 0.0, -180.125, 0.0, -0.25, 90.125)) as dst:
        dst.write(daily_utci_degc, 1)
    daily_mean_tifs.append(os.path.abspath(os.path.join(data_dir, os.path.splitext(file)[0]+'_daily_edit.tif')))
    print(daily_mean_tifs)


def find_same_month(file_list, target_year, target_month):
    """Utility for matching files of the same month and year to process

       Params:
            file_list (list): list of files to look through
            target_year (string): year to find files for - YYYY format
            target_month (string): month to find files for - MM format

        Returns: list of file names
    """
    target_month_list = []
    for f in file_list:
        month_match = fnmatch.fnmatch(f, '*_'+target_year+target_month+'*')
        if month_match:
            target_month_list.append(f)
    return target_month_list


def calculate_monthly_mean(tif_list, output_directory, output_filename):
    """Utility to calculate the monthly mean from a list of tifs

       Params:
            tif_list (list): list of daily tif files to process
            output_directory (string): directory to save new tif to
            output_filename (string): filename for the newly created tif

       Returns: monthly mean tif file saved to specified directory
    """
    # read in daily mean tifs using rasterio
    daily_mean_arrays_list = []
    profiles_list = []
    for file in tif_list:
        with rasterio.open(file) as src:
            array = src.read()
            profile = src.profile
            daily_mean_arrays_list.append(array)
            profiles_list.append(profile)

    # calculate the monthly mean from the daily mean tifs
    monthly_mean = np.mean(daily_mean_arrays_list, axis=0)

    # write the monthly mean to a geotiff file, copying the profile information from one of the original tif files
    profile_out = profiles_list[0].copy()
    profile_out.update(dtype=monthly_mean.dtype.name)
    with rasterio.open(os.path.join(output_directory, output_filename), 'w', **profile_out) as dst:
        dst.write(monthly_mean)

    src.close()


# calculate monthly mean and save as a new tif file
processed_data_file = []
for year in years:
    for month in months:
        # call function to match all the daily mean tifs together and process by month
        process_month = find_same_month(daily_mean_tifs, year, month)
        # call function to calculate the monthly means
        if len(process_month) > 0:
            calculate_monthly_mean(process_month, data_dir, 'monthly_mean_utci_'+year+'_'+month+'_edit.tif')
        else:
            print('No data for specified time period')

# generate names for the processed tif files
processed_data_file = ['data/'+ str(mm) for mm in os.listdir(data_dir)
                       if fnmatch.fnmatch(mm, 'monthly_mean_utci_*')]

logger.info('Finished processing data')


'''
Upload processed data to Google Earth Engine
'''
# set up uploading chunk size
# the default setting requires an uploading speed at 10MB/min. Reduce the chunk size, if the network condition is not good.
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024* 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024* 1024  # 5 MB

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

# create an image collection where we will put the processed data files in GEE
image_collection = f'projects/resource-watch-gee/{dataset_name}'
ee.data.createAsset({'type': 'ImageCollection'}, image_collection)

# set image collection's privacy to public
acl = {"all_users_can_read": True}
ee.data.setAssetAcl(image_collection, acl)
print('Privacy set to public.')

# list the bands in each image
band_ids = ['b1']

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
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zipped:
    for file in raw_data_file:
        zipped.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix + os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zipped:
    for file in processed_data_file:
        zipped.write(file, os.path.basename(file), compress_type=zipfile.ZIP_DEFLATED)

# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
