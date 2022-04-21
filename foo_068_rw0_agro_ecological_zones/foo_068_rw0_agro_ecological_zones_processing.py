import os
import urllib.request
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

'''
Download data and save to your data directory

URLs obtained from https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer 
   Under Theme 1: Land and Water Resources
'''

url_list = ['https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2_CRUTS32_Hist_8110_100_avg.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2_ENSEMBLE_rcp4p5_2020s.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2_ENSEMBLE_rcp4p5_2050s.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2_ENSEMBLE_rcp8p5_2020s.tif',
            'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2_ENSEMBLE_rcp8p5_2050s.tif']

# download the data from the source
raw_data_file = []
for url in url_list:
    filename = os.path.join(data_dir, os.path.basename(url))
    # download data and save with new filename in data_dir
    d = urllib.request.urlretrieve(url, filename)
    raw_data_file.append(d)

'''
Process data
'''
# no processing needed, tifs are in correct format
