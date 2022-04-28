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

# dataset name
dataset_name = 'foo_069_rw0_relative_change_crop_yield'

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
