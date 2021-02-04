import os
import pandas as pd
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import cartosql
from collections import OrderedDict
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_to_carto(file, privacy, collision_strategy='skip'):
    '''
    Upload tables to Carto
    INPUT   file: location of file on local computer that you want to upload (string)
            privacy: the privacy setting of the dataset to upload to Carto (string)
            collision_strategy: determines what happens if a table with the same name already exists
            set the parameter to 'overwrite' if you want to overwrite the existing table on Carto
    '''
    # set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
    # set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    # upload dataset to carto
    dataset = dataset_manager.create(file, collision_strategy = collision_strategy)
    logger.info('Carto table created: {}'.format(os.path.basename(file).split('.')[0]))
    # set dataset privacy
    dataset.privacy = privacy
    dataset.save()

def create_carto_schema(df):
    '''
    Function to create a dictionary of column names and data types
    in order to the upload the data to Carto
    INPUT   df: dataframe storing the data (dataframe)
    RETURN  ouput: an ordered dictionary (dictionary of strings)
    '''
    # create an empty list to store column names
    list_cols = []
    # get column names and types for data table
    # column types should be one of the following: geometry, text, numeric, timestamp
    for col in list(df):
        # if the column type is float64 or int64, assign the column type as numeric
        if (df[col].dtypes  == 'float')| (df[col].dtypes  == 'int'):
            list_cols.append((col, 'numeric'))
        # if the column type is geometry, assign the column type as geometry
        elif col  == 'geometry':
            list_cols.append(('the_geom', 'geometry'))
        # for all other columns assign them as text
        else:
            list_cols.append((col, 'text'))
    # create an ordered dictionary using the list
    output = OrderedDict(list_cols)

    return output

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
    if cartosql.tableExists(table, user=os.getenv('CARTO_WRI_RW_USER'), key=os.getenv('CARTO_WRI_RW_KEY')):
        # if the table does exist, get a list of all the values in the id_field column
        print('Carto table already exists.')
    else:
        # if the table does not exist, create it with columns based on the schema input
        print('Table {} does not exist, creating'.format(table))
        cartosql.createTable(table, schema, user=os.getenv('CARTO_WRI_RW_USER'), key=os.getenv('CARTO_WRI_RW_KEY'))
        # if a unique ID field is specified, set it as a unique index in the Carto table; when you upload data, Carto
        # will ensure no two rows have the same entry in this column and return an error if you try to upload a row with
        # a duplicate unique ID
        if id_field:
            cartosql.createIndex(table, id_field, unique=True, user=os.getenv('CARTO_WRI_RW_USER'), key=os.getenv('CARTO_WRI_RW_KEY'))
        # if a time_field is specified, set it as an index in the Carto table; this is not a unique index
        if time_field:
            cartosql.createIndex(table, time_field, user=os.getenv('CARTO_WRI_RW_USER'), key=os.getenv('CARTO_WRI_RW_KEY'))

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

def shapefile_to_carto(table_name, schema, gdf, privacy):
    '''
    Function to upload a shapefile to Carto
    Note: Shapefiles can also be zipped and uploaded to Carto through the upload_to_carto function
          Use this function when several shapefiles are processed in one single script and need
          to be uploaded to separate Carto tables
          The function should also be used when the table is too large to be exported as a shapefile
    INPUT table_name: the name of the newly created table on Carto (string)
          schema: a dictionary of column names and data types in order to upload data to Carto (dictionary)
          gdf: a geodataframe storing all the data to upload (geodataframe)
          privacy: the privacy setting of the dataset to upload to Carto (string)
    '''
    # create a copy of the geodataframe
    gdf_converted = gdf.copy()
    # convert the geometry of the geodataframe copy to geojsons
    gdf_converted['geometry'] = convert_geometry(gdf_converted.geometry)
    # insert the rows contained in the geodataframe copy to the empty new table on Carto
    for index, row in gdf_converted.iterrows():
        # Carto does not accept Nans for numeric columns; convert them to None
        row = row.where(pd.notnull(row), None)
        cartosql.insertRows(table_name, schema.keys(), schema.values(), [row.values.tolist()], user=os.getenv('CARTO_WRI_RW_USER'), key=os.getenv('CARTO_WRI_RW_KEY'))

    # Change privacy of table on Carto
    #set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
    #set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    #set dataset privacy
    dataset = dataset_manager.get(table_name)
    dataset.privacy = privacy
    dataset.save()
