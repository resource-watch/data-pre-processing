import pandas as pd
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import zipfile
from zipfile import ZipFile
import logging
import glob
import shutil
import geopandas as gpd

  
# set up logging
# get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of table on Carto where you want to upload data
# this should be a table name that is not currently in use
dataset_name = 'com_011_rw1_maritime_boundaries'

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Data can be downloaded at the following link:
https://www.marineregions.org/downloads.php
Expand the 'Maritime Boundaries v11' folder under the Shapefiles list. 
Download the Shapefiles of 'World EEZ v11', 'World 24 Nautical Miles Zone (Contiguous Zone) v3', and 'World 12 Nautical Miles Zone (Territorial Seas) v3' after providing the user information.
'''
# the path to the downloaded data file in the Downloads folder
download = glob.glob(os.path.join(os.path.expanduser("~"), 'Downloads', 'World_*.zip'))

# move this file into your data directory
raw_data_file = [os.path.join(data_dir, os.path.basename(download_file)) for download_file in download]
for download_file, raw_data in zip(download, raw_data_file):
    shutil.move(download_file,raw_data)

# unzip source data
raw_data_file_unzipped = [raw_data.split('.')[0] for raw_data in raw_data_file]
zip_ref = [ZipFile(raw_data, 'r') for raw_data in raw_data_file]
for zip_ref_file, raw_data_unzipped in zip(zip_ref,raw_data_file_unzipped):
    zip_ref_file.extractall(raw_data_unzipped)
    zip_ref_file.close()

'''
Process data
'''
# load in the three polygon shapefiles
# territorial seas (12NM) shapefile
shp_12nm = glob.glob(os.path.join(raw_data_file_unzipped[0], 'World_12NM_v3_20191118/eez_12nm_v3.shp'))[0]
gdf_12nm = gpd.read_file(shp_12nm)
# exclusive economic zones (200NM) shapefile
shp_eez = glob.glob(os.path.join(raw_data_file_unzipped[1], 'World_EEZ_v11_20191118/eez_v11.shp'))[0]
gdf_eez = gpd.read_file(shp_eez)
# contiguous zones (24NM) shapefile
shp_24nm = glob.glob(os.path.join(raw_data_file_unzipped[2], 'World_24NM_v3_20191118/eez_24nm_v3.shp'))[0]
gdf_24nm = gpd.read_file(shp_24nm)

# stack the three geopandas dataframes on top of each other
gdf = pd.concat([gdf_eez, gdf_12nm,gdf_24nm], axis=0, sort=False)

# reproject geometries to epsg 4326
gdf['geometry'] = gdf['geometry'].to_crs(epsg=4326)

# create an index column to use as cartodb_id
gdf['cartodb_id'] = pd.DataFrame(gdf).reset_index(drop=True).index

# reorder the columns
gdf = gdf[['cartodb_id'] + list(gdf)[:-1]]

# convert the column names to lowercase to match the column name requirements of Carto 
gdf.columns = [x.lower() for x in gdf.columns]

# create a path to save the processed shapefile later
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.shp')

# save processed dataset to shapefile
gdf.to_file(processed_data_file, driver='ESRI Shapefile')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    for file in raw_data_file:
        zip.write(file, os.path.basename(file),compress_type= zipfile.ZIP_DEFLATED)
# upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
# find all the necessary components of the shapefile 
processed_data_files = glob.glob(os.path.join(data_dir, dataset_name + '_edit.*'))
with ZipFile(processed_data_dir,'w') as zip:
     for file in processed_data_files:
        zip.write(file, os.path.basename(file))
# upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))

'''
Upload processed data to Carto
'''
# upload the shapefile to Carto
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_dir, 'LINK')