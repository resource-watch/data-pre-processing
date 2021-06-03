import ee
import os
from google.cloud import storage
from google_drive_downloader import GoogleDriveDownloader as gdd
import logging
from zipfile import ZipFile
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud

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
dataset_name = 'cli_050-059_066-075_nexgddp_and_loca'
logger.info('Executing script for dataset: ' + dataset_name)

data_dir = util_files.prep_dirs(dataset_name)
logger.debug('Data directory relative path: '+data_dir)
logger.debug('Data directory absolute path: '+os.path.abspath(data_dir))

'''
Download data and save to your data directory
'''

# download nex-gddp data
logger.info('Downloading raw data: nex-gddp')
file_id = '1h0nwRh64nWH21zsiluBqLqMPNlGBxWqY'
destination = os.path.join(data_dir,'nexgddp.zip')

gdd.download_file_from_google_drive(file_id=file_id,
                                    dest_path=destination,
                                    unzip=True)

# download loca data
logger.info('Downloading raw data: loca')
file_id = '17PNARUvNMDxjT1ALOJQqbmWUK5hxsDbL'
destination = os.path.join(data_dir,'loca.zip')

gdd.download_file_from_google_drive(file_id=file_id,
                                    dest_path=destination,
                                    unzip=True)

'''
Process data and upload processed data to Google Earth Engine
'''

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# define indicators, scenarios, datasets to iterate through in processing
temp_indicators = [
    'annual_tasmin',
    'annual_tasmax',
    'tavg-tasmin_tasmax',
    'hdd65f-tasmin_tasmax',
    'cdd65f-tasmin_tasmax',
    'frostfree_tasmin',
    'gt-q99_tasmax'
]

pr_indicators = [
    'dryspells_pr',
    'annual_pr',
    'gt-q99_pr',
]

all_indicators = temp_indicators + pr_indicators

scenarios = [
    'rcp45',
    'rcp85'
]

datasets = [
    'nexgddp',
    'loca'
]

# define start and end year that each data file is centered around
startyear = 2000
endyear = 2080

def raster_template(ch, i, s, y1, y2, d):
    '''
    generate file name for tif
    INPUT   ch: type of change calcuation - abs, diff, ch (string)
            i: indicator measured by data (string)
            s: climate scenario of data (string)
            y1: first year of 30-yr period represented by file (string)
            y2: last year of 30-yr period represented by file (string)
            d: dataset file comes from - loca, nexgddp (string)
    RETURN  name of raster file (string)
    '''
    pfx = 'stacked'
    if i in ['annual_tasmin','annual_tasmax','tavg-tasmin_tasmax'] and ch == 'abs':
        pfx += '-degC'
    elif i in ['annual_pr'] and ch == 'abs':
        pfx += '-mmyr'
    return f'{pfx}-{ch}-{i}_{s}_ens_{y1}-{y2}_{d}.tif'

for dataset in datasets:
    for indicator in all_indicators:
        image_collection = f'projects/resource-watch-gee/{dataset}/{dataset}_{indicator}'
        # create IC
        ee.data.createAsset({'type': 'ImageCollection'}, image_collection)
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(image_collection, acl)
        logger.info('Privacy set to public.')

        # define changes depending on type of indicator
        if indicator in temp_indicators:
            changes = ['abs', 'diff']
        elif indicator in pr_indicators:
            changes = ['abs', 'ch']

        for scenario in scenarios:
            for y in range(startyear, endyear+1, 10):
                # define start and end years for each file
                y1 = y - 15
                y2 = y + 15
                for change in changes:
                    # get file name
                    f = raster_template(change, indicator, scenario, y1, y2, dataset)
                    file = os.path.join(data_dir, f)
                    dataset_name = f'{dataset}_{scenario}_{indicator}_{change}_{y1}_{y2}'

                    '''
                    Upload processed data to Google Earth Engine
                    '''
                    logger.info('Uploading processed data to Google Cloud Storage.')

                    # upload local files to Google Cloud Storage
                    gs_uris = util_cloud.gcs_upload(file, os.path.join(dataset, dataset_name))

                    logger.info('Uploading processed data to Google Earth Engine.')

                    # set pyramiding policy for GEE upload
                    pyramiding_policy = 'MEAN'  # check

                    # name bands according to variable names in original netcdf
                    bands = ['q25', 'q50', 'q75']
                    # create manifests for upload to GEE
                    band_manifest = [{'id': band, 'tileset_band_index': bands.index(band), 'tileset_id': os.path.basename(gs_uris[0]).split('.')[0],
                                      'pyramidingPolicy': pyramiding_policy} for band in bands]

                    asset_name = f'{image_collection}/{dataset_name}'
                    manifest = util_cloud.gee_manifest_complete(asset_name, gs_uris[0], band_manifest)

                    properties = {
                        'RCP': scenario[-2] + '.' + scenario[-1],
                        'change_vs_absolute': change
                    }
                    manifest['properties'] = properties
                    # upload from GCS to GEE
                    util_cloud.gee_ingest(manifest, public=True)
                    # delete files from GCS
                    util_cloud.gcs_remove(gs_uris, gcs_bucket=gcs_bucket)

                    logger.info('Files deleted from Google Cloud Storage.')

                    '''
                    Upload original data and processed data to Amazon S3 storage
                    '''
                    # amazon storage info
                    aws_bucket = 'wri-public-data'
                    s3_prefix = 'resourcewatch/raster/'

                    logger.info('Uploading processed data to S3.')

                    # Copy the processed data into a zipped file to upload to S3
                    processed_data_dir = os.path.join(dataset_name+'_edit.zip')
                    with ZipFile(processed_data_dir,'w') as zip:
                        zip.write(file, os.path.basename(file))
                    # Upload processed data file to S3
                    uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))