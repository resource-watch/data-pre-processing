import geopandas as gpd
import os
import pyproj
from shapely.ops import transform
import urllib.request
import sys

utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)

from cartoframes.auth import set_default_credentials
from cartoframes import to_carto, update_privacy_table
import util_files
import util_cloud
from zipfile import ZipFile
import logging


# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: 
    logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'ocn_027c_rw0_wastewater_watersheds'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'https://knb.ecoinformatics.org/knb/d1/mn/v2/object/urn%3Auuid%3Aaf8d0bd6-dc0c-4149-a3cd-93b5aed71f7c'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'N_PourPoint_And_Watershed.zip')
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()


'''
Process data
'''

# load in the polygon shapefile
shapes = os.path.join(raw_data_file_unzipped, 'effluent_N_watersheds_all.shp')
gdf = gpd.read_file(shapes)

# convert the data type of columns to integer 
for col in gdf.columns[1:9]:
    gdf[col] = gdf[col].fillna(0).astype('int')

# convert geometry from esri 54009 to epsg 4326 for display on carto
transformer = pyproj.Transformer.from_crs('esri:54009', 'epsg:4326', always_xy=True).transform
for i in range(len(gdf['geometry'])):
    polygon = gdf['geometry'][i]
    gdf['geometry'][i] = transform(transformer, polygon)



'''
Upload processed data to Carto
'''

logger.info('Uploading processed data to Carto.')

# authenticate carto account
CARTO_USER = os.getenv('CARTO_WRI_RW_USER')
CARTO_KEY = os.getenv('CARTO_WRI_RW_KEY')
set_default_credentials(username=CARTO_USER, base_url="https://{user}.carto.com/".format(user=CARTO_USER),api_key=CARTO_KEY)

# upload data frame to Carto
to_carto(gdf, dataset_name + '_edit', if_exists='replace')

# set privacy to 'link' so table is accessible but not published
update_privacy_table(dataset_name + '_edit', 'link')


'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

