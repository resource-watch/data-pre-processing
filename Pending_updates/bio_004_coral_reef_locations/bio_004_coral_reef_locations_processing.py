import geopandas as gpd
import glob
import os
import urllib.request
from collections import OrderedDict
import cartosql
from zipfile import ZipFile
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient


# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'bio_004_coral_reef_locations' 

# set the directory that you are working in with the path variable
# you can use an environmental variable, as we did, or directly enter the directory name as a string
# example: path = '/home/cli_029a_vulnerability_to_cc
path = os.path.join(os.getenv('PROCESSING_DIR'), dataset_name)
# move to this directory
os.chdir(path)

# create a new sub-directory within your specified dir called 'data'
data_dir = 'data'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)

'''
Download data and save to your data directory
'''
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

# convert the data type of column 'PROTECT' and 'PROTECT_FE' to integer
gdf['PROTECT'] = gdf['PROTECT'].astype(int)
gdf['PROTECT_FE'] = gdf['PROTECT_FE'].astype(int)
gdf['METADATA_I'] = gdf['METADATA_I'].astype(int)


# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')

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

# column names and types for data table
# column names should be lowercase
# column types should be one of the following: geometry, text, numeric, timestamp

CARTO_SCHEMA = OrderedDict([
    ('cartodb_id', 'numeric'),
    ('LAYER_NAME', 'text'),
    ('METADATA_I', 'numeric'),
    ('PARENT_ISO', 'text'),
    ('ISO3', 'text'),
    ('SUB_LOC','text'),
    ('ORIG_NAME', 'text'),
    ('FAMILY', 'text'),
    ('GENUS', 'text'),
    ('SPECIES', 'text'),
    ('DATA_TYPE', 'text'),
    ('START_DATE', 'text'),
    ('END_DATE', 'text'),
    ('DATE_TYPE', 'text'),
    ('PROTECT', 'numeric'),
    ('PROTECT_FE', 'numeric'),
    ('VERIF', 'text'),
    ('PROTECT_ST', 'text'),
    ('NAME', 'text'),
    ('LOC_DEF', 'text'),
    ('SURVEY_MET', 'text'),
    ('GIS_AREA_K', 'numeric'),
    ('Shape_Leng', 'numeric'),
    ('Shape_Area', 'numeric'),
    ('REP_AREA_K', 'text'),
    ('the_geom', 'geometry')
    ])
    
# create empty table for dataset on Carto
checkCreateTable(os.path.basename(processed_data_file).split('.')[0], CARTO_SCHEMA)

# create an index column to use as cartodb_id
gdf['id'] = gdf.index

# reorder the columns 
gdf = gdf[['id',
                       'LAYER_NAME',
                       'METADATA_I',
                       'PARENT_ISO',
                       'ISO3',
                       'SUB_LOC',
                       'ORIG_NAME',
                       'FAMILY',
                       'GENUS',
                       'SPECIES',
                       'DATA_TYPE',
                       'START_DATE',
                       'END_DATE',
                       'DATE_TYPE',
                       'PROTECT',
                       'PROTECT_FE',
                       'VERIF',
                       'PROTECT_ST',
                       'NAME',
                       'LOC_DEF',
                       'SURVEY_MET',
                       'GIS_AREA_K',
                       'Shape_Leng',
                       'Shape_Area',
                       'REP_AREA_K',
                       'geometry']]

#save processed dataset to shapefile
gdf.to_file(processed_data_file,driver='ESRI Shapefile')

# convert the geometry of the file from shapely to geojson
gdf['geometry'] = convert_geometry(gdf['geometry'])


# upload the shapefile to the empty carto table
cartosql.insertRows(dataset_name+'_edit', CARTO_SCHEMA.keys(),CARTO_SCHEMA.values(), gdf.values.tolist(), user=CARTO_USER, key=CARTO_KEY)

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




