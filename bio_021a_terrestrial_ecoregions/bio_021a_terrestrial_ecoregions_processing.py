import geopandas as gpd
import glob
import requests
import os
import urllib.request
from collections import OrderedDict
import cartosql
from zipfile import ZipFile
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
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


# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'bio_021a_terrestrial_ecoregions' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')

# insert the url used to download the data from the source website
url = 'https://opendata.arcgis.com/datasets/7b7fb9d945544d41b3e7a91494c42930_0.zip?outSR=%7B%22latestWkid%22%3A3857%2C%22wkid%22%3A102100%7D' #check

# download the data from the source
r = requests.get(url)
raw_data_file = os.path.join(data_dir, 'Terrestrial_Ecoregions-shp.zip')
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
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, '*.shp'))[0]
gdf = gpd.read_file(shapefile)

# Reproject geometries to epsg 4326
gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)

# create an index column to use as cartodb_id
gdf['cartodb_id'] = gdf.index

# reorder the columns
gdf = gdf[['cartodb_id'] + list(gdf)[:-1]]

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')

#save processed dataset to shapefile
gdf.to_file(processed_data_file,driver='ESRI Shapefile', schema = {'properties': OrderedDict([('cartodb_id','int:3'),
              ('FID', 'int:3'),
              ('ECO_ID_U', 'int:5'),
              ('ECO_CODE', 'str:6'),
              ('ECO_NAME', 'str:87'),
              ('ECO_NUM', 'int:2'),
              ('ECODE_NAME', 'str:73'),
              ('CLS_CODE', 'int:4'),
              ('ECO_NOTES', 'str:112'),
              ('WWF_REALM', 'str:2'),
              ('WWF_REALM2', 'str:11'),
              ('WWF_MHTNUM', 'int:2'),
              ('WWF_MHTNAM', 'str:60'),
              ('RealmMHT', 'str:4'),
              ('ER_UPDATE', 'str:8'),
              ('ER_DATE_U', 'str:10'),
              ('ER_RATION', 'str:75'),
              ('SOURCEDATA', 'str:50'),
              ('SHAPE_Leng', 'float:30.5'),
              ('SHAPE_Area', 'float:30.5')]),
 'geometry': 'Polygon'})

'''
Upload processed data to Carto
'''
# Carto username and API key for account where we will store the data
CARTO_USER = os.getenv('CARTO_WRI_RW_USER')
CARTO_KEY = os.getenv('CARTO_WRI_RW_KEY')

def checkCreateTable(table, schema, id_field='', time_field=''):
    '''
    Create the table if it does not exist, and pull list of IDs already in the table if it does
    INPUT   table: Carto table to check or create (string)
            schema: dictionary of column names and types, used if we are creating the table for the first time (dictionary)
            id_field: optional, name of column that we want to use as a unique ID for this table; this will be used to compare the
                    source data to the our table each time we run the script so that we only have to pull data we
                    haven't previously uploaded (string)
            time_field:  optional, name of column that will store datetime information (string)
    '''
    # check it the table already exists in Carto
    if cartosql.tableExists(table, user=CARTO_USER, key=CARTO_KEY):
        # if the table does exist, get a list of all the values in the id_field column
        print('Carto table already exists.')
    else:
        # if the table does not exist, create it with columns based on the schema input
        print('Table {} does not exist, creating'.format(table))
        cartosql.createTable(table, schema, user=CARTO_USER, key=CARTO_KEY)
        # if a unique ID field is specified, set it as a unique index in the Carto table; when you upload data, Carto
        # will ensure no two rows have the same entry in this column and return an error if you try to upload a row with
        # a duplicate unique ID
        if id_field:
            cartosql.createIndex(table, id_field, unique=True, user=CARTO_USER, key=CARTO_KEY)
        # if a time_field is specified, set it as an index in the Carto table; this is not a unique index
        if time_field:
            cartosql.createIndex(table, time_field, user=CARTO_USER, key=CARTO_KEY)

def convert_geometry(geometries):
    '''
    Function to convert shapely geometries to geojsons
    INPUT   geometries: shapely geometries (list of shapely geometries)
    RETURN  output: geojsons (list of geojsons)
    '''
    output = []
    for geom in geometries:
        output.append(geom.__geo_interface__)
    return output

def carto_schema(dataframe):
    '''
    Function to create a dictionary of column names and data types in order to the upload the data to Carto
    INPUT   dataframe: the geopandas dataframe containing the data
    RETURN  ouput: an ordered dictionary
    '''
    list_cols = []
    # column names and types for data table
    # column types should be one of the following: geometry, text, numeric, timestamp
    for col in list(dataframe):
        if (dataframe[col].dtypes  == 'float64')| (dataframe[col].dtypes  == 'int64'):
            list_cols.append((col, 'numeric'))
        elif col  == 'geometry':
            list_cols.append(('the_geom', 'geometry'))
        else:
            list_cols.append((col, 'text'))
    output = OrderedDict(list_cols)
    return output

# create empty table for dataset on Carto
CARTO_SCHEMA = carto_schema(gdf)
checkCreateTable(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA)

# convert the geometry of the file from shapely to geojson
gdf['geometry'] = convert_geometry(gdf['geometry'])

# upload the shapefile to the empty carto table
cartosql.insertRows(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA.keys(), CARTO_SCHEMA.values(), gdf.values.tolist(), user=CARTO_USER, key=CARTO_KEY)

# Change privacy of table on Carto
#set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
#set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)
#set dataset privacy to 'Public with link'
dataset = dataset_manager.get(dataset_name+'_edit')
dataset.privacy = 'LINK'
dataset.save()
logger.info('Privacy set to public with link.')

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

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
# Find al the necessary components of the shapefile 
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
     for file in processed_data_files:
        zip.write(file, os.path.basename(file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
