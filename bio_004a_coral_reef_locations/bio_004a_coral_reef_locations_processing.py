import geopandas as gpd
import glob
import os
import shutil
from shapely.geometry import Polygon
import urllib.request
from collections import OrderedDict
import cartosql
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
from zipfile import ZipFile
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
dataset_name = 'bio_004a_coral_reef_locations'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
logger.info('Downloading raw data')
# insert the url used to download the data from the source website
url = 'http://wcmc.io/WCMC_008'

# download the data from the source
raw_data_file = os.path.join(data_dir, 'WCMC008_CoralReefs2018_v4.zip')
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
shapefile = glob.glob(os.path.join(raw_data_file_unzipped, '14_001_WCMC008_CoralReefs2018_v4', '01_Data', '*Py_v4.shp'))[0]
gdf = gpd.read_file(shapefile)

# convert the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integer
gdf['PROTECT'] = gdf['PROTECT'].astype(int)
gdf['PROTECT_FE'] = gdf['PROTECT_FE'].astype(int)
gdf['METADATA_I'] = gdf['METADATA_I'].astype(int)

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')
# create an index column to use as cartodb_id
gdf['cartodb_id'] = gdf.index

# reorder the columns
gdf = gdf[['cartodb_id'] + list(gdf)[:-1]]

# save processed dataset to shapefile
gdf.to_file(processed_data_file,driver='ESRI Shapefile')

'''
Create a mask for the data
To create a mask for the dataset, you need to first create a 10km buffer around each coral reef polygon
Considering the time and computation power needed to complete this operation, 
we recommend you create the buffer in Google Earth Engine and export it as a shapefile to Google Drive
You will then be able to download the buffer shapefile from your Google Drive
'''
# download the shapefile from the Google Drive
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'drive*.zip'))[0]
# Move this file into your data directory
buffer_zipped = os.path.join(data_dir, os.path.basename(download))
shutil.move(download, buffer_zipped)

# unzip the buffer data 
buffer_unzipped = buffer_zipped.split('.')[0]
zip_ref = ZipFile(buffer_zipped, 'r')
zip_ref.extractall(buffer_unzipped)
zip_ref.close()

# read the shapefile that contains 10km buffer around the dataset as a geopandas data frame
gdf_buffer = gpd.read_file(os.path.join(buffer_unzipped, dataset_name+'_buffer.shp'), encoding='latin-1')

# create a new field 'dissolve_id' 
gdf_buffer['dissolve_id'] = 1
# dissolve the buffered polygons into a single polygon
gdf_dis = gdf_buffer.dissolve(by='dissolve_id')

# we only need the geometry of the buffered coral reef polygon to create a mask 
# therefore we remove columns other than the 'geometry' column and reset the index 
gdf_dis = gpd.GeoDataFrame(gdf_dis.geometry).reset_index(drop = True)

# create a polygon that covers the entire world 
polygon = Polygon([(-180, 90), (-180, -90), (180, -90), (180, 90)])
# convert the polygon into a geopandas dataframe 
poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=gdf_buffer.crs)

# create a mask by finding the difference between the world polygon and the buffered coral reef polygon
gdf_mask = gpd.overlay(poly_gdf, gdf_dis, how='difference')
# assign the correct headers to the mask dataframe 
gdf_mask.columns = ['cartodb_id', 'geometry']

# convert the data type of the column 'cartodb_id' in the mask dataframe to integer
gdf_mask.cartodb_id = gdf_mask.cartodb_id.astype(int)
# export the mask as a shapefile 
processed_data_mask = os.path.join(data_dir, dataset_name+'_mask.shp')
gdf_mask.to_file(processed_data_mask, driver='ESRI Shapefile')

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
        if (dataframe[col].dtype  == 'float')| (dataframe[col].dtype  == 'int'):
            list_cols.append((col, 'numeric'))
        elif col  == 'geometry':
            list_cols.append(('the_geom', 'geometry'))
        else:
            list_cols.append((col, 'text'))
    output = OrderedDict(list_cols)
    return output

# create empty table for dataset on Carto
CARTO_SCHEMA_data = carto_schema(gdf)
checkCreateTable(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA_data)

# create empty table for the mask on Carto
CARTO_SCHEMA_mask = carto_schema(gdf_mask)
checkCreateTable(os.path.basename(processed_data_mask).split('.')[0], CARTO_SCHEMA_mask)

# convert the geometry of the file from shapely to geojson
gdf['geometry'] = convert_geometry(gdf['geometry'])

# convert the geometry of the mask from shapely to geojson
gdf_mask['geometry'] = convert_geometry(gdf_mask['geometry'])

# upload the processed data to the empty carto table
cartosql.insertRows(dataset_name+'_edit', CARTO_SCHEMA_data.keys(),CARTO_SCHEMA_data.values(), gdf.values.tolist(), user=CARTO_USER, key=CARTO_KEY)

# upload the mask data to the empty carto table
cartosql.insertRows(dataset_name + '_mask', CARTO_SCHEMA_mask.keys(),CARTO_SCHEMA_mask.values(), gdf_mask.values.tolist(), user=CARTO_USER, key=CARTO_KEY)

# Change privacy of the two tables on Carto
# set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
# set up dataset manager with authentication
dataset_manager = DatasetManager(auth_client)

# set dataset privacy to 'Public with link'
dataset = dataset_manager.get(dataset_name+'_edit')
dataset.privacy = 'LINK'
dataset.save()
logger.info('Privacy set to public with link.')

# set mask dataset privacy to 'Public with link'
mask = dataset_manager.get(dataset_name+'_mask')
mask.privacy = 'LINK'
mask.save()
logger.info('Privacy set to public with link.')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
    zip.write(processed_data_mask, os.path.basename(processed_data_mask))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
