import os
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
from collections import OrderedDict
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# username and api key of the carto account 
CARTO_USER = os.getenv('CARTO_WRI_RW_USER')
CARTO_KEY = os.getenv('CARTO_WRI_RW_KEY')

def upload_to_carto(file, privacy, *tags:str, collision_strategy='skip'):
    '''
    Upload tables to Carto
    INPUT   file: location of file on local computer that you want to upload (string)
            privacy: the privacy setting of the dataset to upload to Carto (string)
            tags: add one or more tags(string) to the dataset, default is "rw"
            collision_strategy: determines what happens if a table with the same name already exists
            due to changes in carto api if set to skip and table name already exists it will raise an exception
            set the parameter to 'overwrite' if you want to overwrite the existing table on Carto
    '''
    # set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=CARTO_KEY, base_url="https://{user}.carto.com/".format(user=CARTO_USER))
    # set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    # upload dataset to carto
    try:
        dataset = dataset_manager.create(file, collision_strategy = collision_strategy)
        logger.info('Carto table created: {}'.format(os.path.basename(file).split('.')[0]))
    except ValueError:
        logging.exception("Table probably already existing, try setting collision_strategy to overwrite or using another name")
        # If exception is raised terminate program
        sys.exit(1)
    # adding tags
    # pass one or more tags as strings, default is "rw"
    if tags:
        new_tags = []
        for tag in tags:
            new_tags.append(tag)
    else:
        new_tags = ['rw']
    # set up tags     
    dataset.tags = new_tags
    for tag in new_tags:
        logger.info('Adding the following tag to table:{}'.format(tag))
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

def convert_geometry(geom):
    '''
    Function to convert shapely geometries to geojsons
    INPUT   geom: shapely geometry 
    RETURN  geojsons 
    '''
    # if it's a polygon
    if geom.geom_type == 'Polygon':
        return geom.__geo_interface__
    # if it's a multipoint series containing only one point
    elif (geom.geom_type == 'MultiPoint') & (len(geom) == 1):
        return geom[0].__geo_interface__
    else:
        return geom.__geo_interface__


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
    if table in getTables(user=CARTO_USER, key=CARTO_KEY):
        # if the table does exist, get a list of all the values in the id_field column
        print('Carto table already exists.')
    else:
        # if the table does not exist, create it with columns based on the schema input
        print('Table {} does not exist, creating'.format(table))
        createTable(table, schema, user=CARTO_USER, key=CARTO_KEY)
        # if a unique ID field is specified, set it as a unique index in the Carto table; when you upload data, Carto
        # will ensure no two rows have the same entry in this column and return an error if you try to upload a row with
        # a duplicate unique ID
        if id_field:
            createIndex(table, id_field, unique=True, user=CARTO_USER, key=CARTO_KEY)
        # if a time_field is specified, set it as an index in the Carto table; this is not a unique index
        if time_field:
            createIndex(table, time_field, user=CARTO_USER, key=CARTO_KEY)

def insert_carto_query(row, schema, table_name):
    '''
    Build the sql query that inserts a row to carto 
    INPUT   row: row of data to insert to carto (series)
            table_name: the name of the newly created table on Carto (string)
            schema: a dictionary of column names and data types in order to upload data to Carto (dictionary)
    RETURN  sql query that can be included in a post request (string)
    '''
    # replace all null values with None
    row = row.where(row.notnull(), None)
    insert_exception = None
    # convert the geometry in the geometry column to geojsons
    row['geometry'] = convert_geometry(row['geometry'])
    # construct the sql query to upload the row to the carto table
    fields = schema.keys()
    values = _dumpRows([row.values.tolist()], tuple(schema.values()))
    return 'INSERT INTO "{}" ({}) VALUES {}'.format(table_name, ', '.join(fields), values)

def insert_carto_send(sql):
    '''
    Send a request to carto API
    INPUT   sql: sql query that can be included in a post request (string)
    OUTPUT  index of the row sent (number)
    '''
    # maximum attempts to make
    n_tries = 5
    # sleep time between each attempt   
    retry_wait_time = 6

    for i in range(n_tries):
        try:
            # send the request 
            r = requests.post('https://{}.carto.com/api/v2/sql'.format(CARTO_USER), json={'api_key': CARTO_KEY,'q': sql})
            r.raise_for_status()
        except Exception as e: # if there's an exception do this
            insert_exception = e
            logging.warning('Attempt #{} to upload unsuccessful. Trying again after {} seconds'.format(i, retry_wait_time))
            logging.debug('Exception encountered during upload attempt: '+ str(e))
            time.sleep(retry_wait_time)
        else: # if no exception do this
            return row.index
    else:
        # this happens if the for loop completes, ie if it attempts to insert row n_tries times without succeeding
        logging.error('Upload has failed after {} attempts'.format(n_tries))
        logging.error('Problematic row: '+ str(row))
        logging.error('Raising exception encountered during last upload attempt')
        logging.error(insert_exception)
        raise insert_exception

def shapefile_to_carto(table_name, schema, gdf, privacy = 'LINK'):
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
    # initiate a ThreadPoolExecutor with 10 workers 
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        # create an empty list to store the index of the rows uploaded
        all_ids = []
        for index, row in gdf.iterrows():
            # build the sql query to send to Carto 
            query = insert_carto_query(row, schema, table_name)
            # submit the task to the executor
            futures.append(executor.submit(insert_carto_send, query))
        for future in as_completed(futures):
            all_ids.append(future.result())
    logging.info('Upload of {} rows complete!'.format(len(all_ids)))

    # Change privacy of table on Carto
    #set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=CARTO_KEY, base_url="https://{user}.carto.com/".format(user=CARTO_USER))
    #set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    #set dataset privacy
    dataset = dataset_manager.get(table_name)
    dataset.privacy = privacy
    dataset.save()
    
def sendSql(sql, user=None, key=None, f='', post=True):
    '''
    Send arbitrary sql and return response object or False
    INPUT   sql: the sql query that will be included in the body of the request (string)
            user: the username of the Carto account (string)
            key: the key for Carto API (string)
            f： the format parameter included in the payload (string)
            post: whether this is a POST request (boolean)
    RETURN  the response from the API
    '''
    # the url to which the request will be sent 
    url = "https://{}.carto.com/api/v2/sql".format(user)
    payload = {
        'api_key': key,
        'q': sql,
    }
    if len(f):
        payload['format'] = f
    logging.debug((url, payload))
    if post:
        r = requests.post(url, json=payload)
    else:
        r = requests.get(url, params=payload)
    r.raise_for_status()
    return r

def getTables(user=None, key=None, f='csv'):
    '''
    Get the list of tables in the Carto account
    INPUT   user: the username of the Carto account (string)
            key: the key for Carto API (string)
            f： the format parameter included in the payload (string)
    RETURN  tables stored on the Carto account (list of strings if f is 'csv' else response object)
    '''
    # send the request to Carto API to fetch the tables stored in the Carto account
    r = sendSql('SELECT * FROM CDB_UserTables()', user, key, f, False)
    if f == 'csv':
        # split the response to get a list of tables 
        return r.text.splitlines()[1:]
    return r

def createTable(table, schema, user=None, key=None):
    '''
    Create table with schema and CartoDBfy table
    INPUT   table: the name of the Carto table to be created (string)
            schema: a dictionary of the column names and types of data stored in them (ordered dictionary)
            user: the username of the Carto account (string)
            key: the key for Carto API (string)
    RETURN  calling the function to CartoDBfy the table if the query to create table has been successfully sent
            otherwise returns False (boolean)
    '''
    items = schema.items() if isinstance(schema, dict) else schema
    defslist = ['{} {}'.format(k, v) for k, v in items]
    sql = 'CREATE TABLE "{}" ({})'.format(table, ','.join(defslist))
    if sendSql(sql, user, key):
        return _cdbfyTable(table, user, key)
    return False

def _cdbfyTable(table, user=None, key=None):
    '''
    CartoDBfy table so that it appears in Carto UI
    INPUT   table: the name of the Carto table (string)
            user: the username of the Carto account (string)
            key: the key for Carto API (string)
    RETURN  calling the function to send Carto API the query to CartoDBfy the table 
    '''
    sql = "SELECT cdb_cartodbfytable('{}','\"{}\"')".format(user, table)
    return sendSql(sql, user, key)

def createIndex(table, fields, unique='', using='', user=None,
                key=None):
    '''
    Create index on table on field(s)
    INPUT   table: the name of the Carto table (string)
            fields: the column(s) based on which the index is created (string or list of strings)
            unique: whether this is unique index (string)
            using: whether the index is created based on column(s) (string)
            user: the username of the Carto account (string)
            key: the key for Carto API (string)
    RETURN  calling the function to send Carto API the query to create index for the table
    '''
    fields = (fields,) if isinstance(fields, str) else fields
    f_underscore = '_'.join(fields)
    f_comma = ','.join(fields)
    unique = 'UNIQUE' if unique else ''
    using = 'USING {}'.format(using) if using else ''
    sql = 'CREATE {} INDEX idx_{}_{} ON {} {} ({})'.format(
        unique, table, f_underscore, table, using, f_comma)
    return sendSql(sql, user, key)

def _escapeValue(value, dtype):
    '''
    Escape value for SQL based on field type
    INPUT   value: the value to be included in the query (can be of different data types as listed below)
            dtype: the data types of the value （string) 
    RETURN  SQL string ready to be included in the query to Carto API (string)
    TYPE         Escaped
    None      -> NULL
    geometry  -> string as is; obj dumped as GeoJSON
    text      -> single quote escaped
    timestamp -> single quote escaped
    varchar   -> single quote escaped
    else      -> as is
    '''
    if value is None:
        return "NULL"
    if dtype == 'geometry':
        # if not string assume GeoJSON and assert WKID
        if isinstance(value, str):
            return value
        else:
            value = json.dumps(value)
            return "ST_SetSRID(ST_GeomFromGeoJSON('{}'),4326)".format(value)
    elif dtype in ('text', 'timestamp', 'varchar'):
        # quote strings, escape quotes, and drop nbsp
        return "'{}'".format(
            str(value).replace("'", "''"))
    else:
        return str(value)
    
def _dumpRows(rows, dtypes):
    '''
    Escapes rows of data to SQL strings
    INPUT   rows: rows of data to convert to SQL strings (list of lists)
            dtypes: the data type of the columns (list of strings)
    RETURN  SQL string ready to be included in the query to Carto API (string)
    '''
    dumpedRows = []
    for row in rows:
        escaped = [
            _escapeValue(row[i], dtypes[i])
            for i in range(len(dtypes))
        ]
        dumpedRows.append('({})'.format(','.join(escaped)))
    return ','.join(dumpedRows)