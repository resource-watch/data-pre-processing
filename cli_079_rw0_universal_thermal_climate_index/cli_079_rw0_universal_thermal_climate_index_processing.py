import os
import sys
import cdsapi
import zipfile
from zipfile import ZipFile
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
from osgeo import gdal
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import rioxarray as rio


# dataset name
dataset_name = 'cli_079_rw0_universal_thermal_climate_index'

# Processing steps
   # loop through bands and convert kelvin to celsius
   # loop through bands and get mean daily UTCI in C
   # loop through daily mean UTCI files and get a monthly average

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = '/Users/alexsweeney/Desktop/data-dir/utci/'  # change for PR
    #util_files.prep_dirs(dataset_name)

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
            '01', '02',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'format': 'zip',
    },
    data_dir+'download.zip')

# unzip source data
with ZipFile('/Users/alexsweeney/Desktop/data-dir/utci/download.zip', 'r') as zip_obj:
    # add filenames to raw_data_file list
    raw_data_file = zip_obj.namelist()
    zip_obj.extractall(data_dir)
    zip_obj.close()

# read in multiple files from data_dir and process
for file in raw_data_file:
    f = netCDF4.Dataset(os.path.join(data_dir, file), 'r')
    # TODO add in processing steps
    print(file)

'''Single netCDF for testing purposes
# use netcdf4 module to read in data
filename = '/Users/alexsweeney/Documents/WRI/data/universal-thermal-climate-index/dataset-derived-utci-historical-19aced01-259c-476e-98c0-8367aff45e7a/ECMWF_utci_20210429_v1.1_con.nc'
f = netCDF4.Dataset(filename, 'r')
'''

# TODO read data to numpy array and calc daily average
# 2. Read data into numpy array and calc daily average, and save to file (?)
# access the utci variable
raw_utci = f.variables['utci'][:]  # dimensions should be (24, 601, 1440)
# convert kelvin to celsius (subtract 273.15)
utci_degc = np.subtract(raw_utci, 273.15)  # should have same dimensions but now in degrees C
# get daily average, use numpy mean to get the average value across the 24 hours (bands)
daily_utci_degc = np.mean(utci_degc, axis=0)  # new dimensions should be (1, 601, 1440) because we collapsed the time into 1


# TODO 3. calc monthly from the daily numpy arrays
# next step would be to average all days for a monthly average
# Create a function with the above steps (converting kelvin to celsius), averaging the hours into 1 24 hour (daily) average, potentially converting to monthly average

# 4. Save processed to geotiffs for upload - numpy to geotiff (libraries that can be used = rasterio, gdal)
# Convert to a geotiff and save file