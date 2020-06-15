#!/usr/bin/env python
# coding: utf-8

# ## Preparation

# #### Import

# In[1]:


import os
import sys
import dotenv
dotenv.load_dotenv(os.path.abspath(os.getenv('RW_ENV')))


# In[2]:


if os.getenv('PROCESSING_DIR') not in sys.path:
    sys.path.append(os.path.abspath(os.getenv('PROCESSING_DIR')))
import util_files
import util_cloud


# In[3]:


# import boto3
# from botocore.exceptions import NoCredentialsError
import urllib
from zipfile import ZipFile
import ee
import subprocess
from google.cloud import storage
from shutil import copyfile
import time


# #### Set/initialize/authenticate general variables

# In[4]:


# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

# initialize ee and eeUtil modules for uploading to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

aws_bucket = 'wri-projects'
s3_prefix = 'resourcewatch/raster/'


# #### Set dataset-specific variables

# In[5]:


# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'ocn_005_historical_cyclone_intensity'

band_ids = ['cy_intensity', 
           ]

# set pyramiding policy for GEE upload
pyramiding_policy = 'MEAN' #check


# ## Execution

# In[6]:


data_dir = util_files.prep_dirs(dataset_name)


# In[7]:


'''
Raw data must be downloaded manually and placed in appropriate folder
'''
# data source page:
#     https://preview.grid.unep.ch/index.php?preview=data&events=cyclones&evcat=4&lang=eng
# access dataset via "DOWNLOAD" option in sidebar, which prompts javascript popup
# download data as GeoTiff
# place resulting zip file in data folder
# expected file name as of june 2020: 
#     cy_intensity_20200408183708_tiff.zip

raw_data_file = os.path.join(data_dir,'cy_intensity_20200408183708_tiff.zip')
print(os.path.abspath(raw_data_file))


# In[8]:


print('Unzip raw data')
with ZipFile(raw_data_file, 'r') as zip:
    namelist = zip.namelist()
    tifnames = [name for name in namelist if '.tif' in name]
    if len(tifnames) != 1:
        raise Exception()
    tifname = tifnames[0]
    zip.extractall(data_dir)
# in this case "processed" data file is just unzipped tif
# but we have to rename it
unprocessed_data_file = (os.path.join(data_dir,tifname))
processed_data_file = os.path.join(data_dir,dataset_name+'.tif')
print (processed_data_file)
copyfile(unprocessed_data_file, processed_data_file)


# In[9]:


print('Uploading processed data to Google Cloud Storage.')
gcs_uris = util_cloud.gcs_upload(processed_data_file, dataset_name, gcs_bucket=gcs_bucket)


# In[10]:


import imp
imp.reload(util_cloud)

print('Uploading processed data to Google Earth Engine.')
# name bands according to variable names in original netcdf
bands = [{'id': band_id, 'tileset_band_index': band_ids.index(band_id), 'tileset_id': dataset_name, 'pyramidingPolicy': pyramiding_policy} for band_id in band_ids]

# Upload processed data file to GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

task_id = util_cloud.gee_ingest(gcs_uris[0], asset=asset_name, bands=bands, public=True)


# In[11]:


util_cloud.gcs_remove(gcs_uris, gcs_bucket=gcs_bucket)
print('Files deleted from Google Cloud Storage.')


# In[12]:


print('Uploading original data to S3.')
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_file, aws_bucket, s3_prefix+os.path.basename(raw_data_file))

print('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))

