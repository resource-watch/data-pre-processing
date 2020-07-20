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
import boto3
from botocore.exceptions import NoCredentialsError

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'bio_021_terrestrial_ecoregions' #check

# set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cli_029a_vulnerability_to_cc'
dir = os.path.join(os.getenv('PROCESSING_DIR'), dataset_name)
#move to this directory
os.chdir(dir)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
    
'''
Download data and save to your data directory
'''
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
gdf.to_file(processed_data_file,driver='ESRI Shapefile')

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
        if (gdf[col].dtypes  == 'float64')| (gdf[col].dtypes  == 'int64'):
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
print('Privacy set to public with link.')

'''
Upload original data and processed data to Amazon S3 storage
'''
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'),
                      aws_secret_access_key=os.getenv('aws_secret_access_key'))
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
with ZipFile(raw_data_dir, 'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))

# Upload raw data file to S3
uploaded = upload_to_aws(raw_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(raw_data_dir))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir, 'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))

# Upload processed data file to S3
uploaded = upload_to_aws(processed_data_dir, 'wri-public-data', 'resourcewatch/'+os.path.basename(processed_data_dir))
