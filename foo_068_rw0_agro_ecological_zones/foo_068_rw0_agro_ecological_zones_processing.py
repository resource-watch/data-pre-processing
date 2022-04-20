import os
import urllib.request
from urllib.parse import urlsplit
import re
import sys
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'foo_068_rw0_agro_ecological_zones'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# list of urls from data source
# urls downloaded from https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer
# under Theme 1: Land and Water Resources
