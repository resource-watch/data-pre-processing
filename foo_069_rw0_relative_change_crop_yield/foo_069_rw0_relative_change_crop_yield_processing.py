import os
import pandas as pd
import requests
import sys
import re
from datetime import datetime
import fnmatch
import json
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import logging

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# dataset name
dataset_name = 'foo_069_rw0_relative_change_crop_yield'

logger.info('Executing script for dataset: ' + dataset_name)

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)


# define get_iso3_list
def get_iso3_list():
    """
    Utility for getting a list of ISO3 country codes from Climate Analytics' Impact Data Explorer API

    Returns:
        List of ISO3 codes
    """
    response = requests.get('https://cie-api.climateanalytics.org/api/meta/')
    data = json.loads(response.content.decode('utf-8'))
    country_list = data['countries']

    iso3_list = []
    for country in country_list:
        iso3 = country['id']
        if len(iso3) < 4:
            iso3_list.append(iso3)
        else:
            None
    return iso3_list


# define get_province_list
def get_province_list(iso_code):
    """
    Utility for getting a list of provinces (admin1 boundaries) for the input ISO3 country code. Gets list from Climate
    Analytics' Impact Data Explorer API

    Returns:
        List of provinces
    """
    response = requests.get('https://cie-api.climateanalytics.org/api/shapes/?iso=' + iso_code)
    data = json.loads(response.content.decode('utf-8'))
    province_list = []
    for key in data['country']['objects']['data']['geometries'][0]['properties']['subregions'].keys():
        province_list.append(key)
    return province_list


# define get data
def get_data(iso3_code, province_code):
    """
    Creates API requests for Change in Rice Yield data from Climate Analytics' Impact Data Explorer API

    Returns:
        CSV downloads to your specified data directory
    """
    # setting up parameters for URL construction
    # note, all scenarios are downloaded in the CSV even though RCP45 is the only one specified in the API call
    payload = {'iso': iso3_code, 'region': province_code, 'scenario': 'rcp45', 'var': 'yield_rice_co2',
               'season': 'annual', 'aggregation_spatial': 'area', 'format': 'csv'}
    r = requests.get('https://cie-api.climateanalytics.org/api/ts/', params=payload, allow_redirects=True)
    try:
        # get info on the filename that would download manually
        d = r.headers.get('content-disposition')
        filename = re.findall('filename=(.+)', d)[0]
        print('Successfully downloaded data for:', province_code)
        # save raw csv to data directory with filename as obtained above
        return open(os.path.join(data_dir, filename), 'wb').write(r.content)
    except:
        print('API returned NULL data, so no file downloaded for:', province_code)


'''
Download data
'''

# create country list for download
iso_list = get_iso3_list()

# create province list for download
admin1_list = [
    {
        'iso': 'IND',
        'admins': get_province_list('IND')
    },
    {
        'iso': 'COL',
        'admins': get_province_list('COL')
    }
]

# get data for admin0 (country) level data
for iso in iso_list:
    prov_code = iso
    get_data(iso, prov_code)

# get data for admin1 (provincial) level data
for admin1 in admin1_list:
    iso = admin1['iso']
    for admin in admin1['admins']:
        get_data(iso, admin)


'''
Process data
'''

# create a list of paths to raw csvs in data directory
raw_data_file = [os.path.abspath(os.path.join(data_dir, p)) for p in os.listdir(data_dir)]

# save raw data file names as a list
raw_data_files_list = [os.path.basename(f) for f in raw_data_file]


# define add country
def add_country(csv_file):
    """ Utility to obtain the ISO code from the CSV header and add it as a value to the new column "country" """
    # access the first rows of raw CSV to obtain the country (ISO3 code)
    header_info = pd.read_csv(csv_file, nrows=2)
    country = header_info['Rice Yield'].values[1]
    # add ISO3 codes to new column "country"
    df['country'] = country


# loop through CSVs and append country and provincial codes to new columns
unioned_data = []
for file in sorted(raw_data_file):
    if file.endswith('.csv'):
        # use fnmatch to find provincial CSVs
        if fnmatch.fnmatch(file, '*.*.csv'):
            # processing for provincial level CSVs
            df = pd.read_csv(file, header=3)
            # add country ISO3 code to df
            add_country(file)
            # next, get the admin1 code from the filename
            s = os.path.basename(file).split('_')
            admin1_code = s[4]
            # add admin1 code to new column "admin1_code"
            df['admin1_code'] = admin1_code
            unioned_data.append(df)
        else:
            # processing for national level CSVs
            df = pd.read_csv(file, header=3)
            # add country ISO3 code to df
            add_country(file)
            # add admin1 info to new column "admin1_code"; inserting None since it's a national level (admin0) data
            df['admin1_code'] = None
            unioned_data.append(df)
    else:
        print('File is not a CSV')

# union all the new dataframes together into a global dataframe
unioned_data = pd.concat(unioned_data)

# continue further processing of the newly concatenated, global dataframe
# create a new column 'datetime' to store years as datetime objects
unioned_data['datetime'] = [datetime(x, 1, 1) for x in unioned_data.year]

# drop unnamed column
unioned_data = unioned_data.drop(unioned_data.columns[[0]], axis=1)

# filter out CAT emissions scenario columns
unioned_data = unioned_data.loc[:, ~unioned_data.columns.str.contains('CAT')]

# filter out NGFS emissions scenario columns
unioned_data = unioned_data.loc[:, ~unioned_data.columns.str.contains('NGFS')]

# replace periods in column headers with underscores
unioned_data.columns = unioned_data.columns.str.replace('[.]', '_', regex=True)

# add underscores between words in column headers
unioned_data.columns = unioned_data.columns.str.replace(' ', '_')

# replace all NaN with None
unioned_data = unioned_data.where((pd.notnull(unioned_data)), None)

# save processed dataset to CSV
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
unioned_data.to_csv(processed_data_file, index=False)

# Note: in the data_dir at this point there should be 187 files: 186 raw CSVs and 1 edited global CSV
