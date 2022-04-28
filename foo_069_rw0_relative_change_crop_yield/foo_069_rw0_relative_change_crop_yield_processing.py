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