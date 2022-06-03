import os
import sys
import cdsapi
from zipfile import ZipFile
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import netCDF4
import numpy as np
import rasterio


# dataset name
dataset_name = 'cli_079_rw0_universal_thermal_climate_index'

# Processing steps
   # loop through bands and convert kelvin to celsius
   # loop through bands and get mean daily UTCI in C
   # loop through daily mean UTCI files and get a monthly average

'''
Download data
'''

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# 1. get data and download to local machine
# access CDS API - more info here: https://cds.climate.copernicus.eu/api-how-to
c = cdsapi.Client()
# example API request for UTCI data (sample of data for testing purposes)
c.retrieve(
    'derived-utci-historical',
    {
        'variable': 'universal_thermal_climate_index',
        'version': '1_1',
        'product_type': 'consolidated_dataset',
        'year': '2022',
        'month': [
            '01', #'02',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            #'07', '08', '09',
            #'10', '11', '12',
            #'13', '14', '15',
            #'16', '17', '18',
            #'19', '20', '21',
            #'22', '23', '24',
            #'25', '26', '27',
            #'28', '29', '30',
            #'31',
        ],
        'format': 'zip',
    },
    os.path.join(data_dir, 'utci_download.zip'))

# unzip source data
with ZipFile('data/utci_download.zip', 'r') as zip_obj:
    # add filenames to raw_data_nc list (list of raw netcdf files)
    raw_data_file = zip_obj.namelist()
    zip_obj.extractall(data_dir)
    zip_obj.close()

# TODO replace periods with underscores in netcdf file names

'''
Process Data
'''
# create a list of paths for the netcdf files
raw_data_file = [os.path.abspath(os.path.join(data_dir, p)) for p in raw_data_file]

# open netcdf files
for file in raw_data_file:
    raw_data = netCDF4.Dataset(os.path.join(data_dir, file), 'r')
    # isolate the universal thermal climate index (utci) variable
    raw_utci = raw_data.variables['utci'][:]  # dimensions should be (24, 601, 1440)
    # convert from kelvin to celsius (subtract 273.15)
    utci_degc = np.subtract(raw_utci, 273.15)
    # get daily average, use numpy mean to get the average value across the 24 hours (bands)
    daily_utci_degc = np.mean(utci_degc, axis=0)
    # save daily average to a new tif file, all metadata is from viewing info from raw_data variable
    with rasterio.open(os.path.join(data_dir, file+'_daily_edit.tif'),
                       'w',
                       driver='GTiff',
                       height=daily_utci_degc.shape[0],
                       width=daily_utci_degc.shape[1],
                       count=1,
                       dtype=daily_utci_degc.dtype,
                       nodata=-9.0e33,
                       transform=(0.25, 0.0, -180.125, 0.0, -0.25, 90.125)) as dst:
        dst.write(daily_utci_degc, 1)

# TODO calculate monthly mean?

# TODO create processed data files list