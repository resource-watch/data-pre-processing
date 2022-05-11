import os
import sys
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
from osgeo import gdal
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import rioxarray as rio



# dataset name
dataset_name = 'cli_xxx_utci'

# Processing steps
   # loop through bands and convert kelvin to celsius
   # loop through bands and get mean daily UTCI in C
   # loop through daily mean UTCI files and get a monthly average

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# investigating netcdf
# use netcdf4 module to read in data
filename = '/Users/alexsweeney/Documents/WRI/data/universal-thermal-climate-index/dataset-derived-utci-historical-19aced01-259c-476e-98c0-8367aff45e7a/ECMWF_utci_20210429_v1.1_con.nc'
f = nc.Dataset(filename, 'r')

# access the utci variable
raw_utci = f.variables['utci'][:]  # dimensions should be (24, 601, 1440)
# convert kelvin to celsius (subtract 273.15)
utci_degc = np.subtract(raw_utci, 273.15)  # should have same dimensions but now in degrees C
# get daily average, use numpy mean to get the average value across the 24 hours (bands)
daily_utci_degc = np.mean(utci_degc, axis=0)  # new dimensions should be (601, 1440) because we collapsed the time into 1
#

# TODO
# next step would be to average all days for a monthly average
# Create a function with the above steps (converting kelvin to celsius), averaging the hours into 1 24 hour (daily) average

# Convert to a geotiff and save file