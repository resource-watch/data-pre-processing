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
import fnmatch

# dataset name
dataset_name = 'cli_079_rw0_universal_thermal_climate_index'

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
    raw_file = zip_obj.namelist()
    zip_obj.extractall(data_dir)
    zip_obj.close()

# create a list of paths for the netcdf files
raw_file = [os.path.abspath(os.path.join(data_dir, p)) for p in raw_file]

# remove dots from filenames and replace with underscores
for rf in raw_file:
    # split path into root and extension
    p = os.path.splitext(rf)
    # isolate the root
    name = p[0]
    # replace the dots with underscores
    nodots = name.replace('.', '_')
    new_name = nodots+p[1]
    # rename files
    os.rename(rf, new_name)

# create raw_data_file list
raw_data_file = [os.path.abspath(os.path.join(data_dir, file)) for file in os.listdir(data_dir) if file.endswith('.nc')]

'''
Process Data
'''

# open netcdf files and calculate daily mean
daily_mean_tifs = []
for file in raw_data_file:
    raw_data = netCDF4.Dataset(file, 'r')
    # isolate the universal thermal climate index (utci) variable
    raw_utci = raw_data.variables['utci'][:]  # dimensions should be (24, 601, 1440)
    # convert from kelvin to celsius (subtract 273.15)
    utci_degc = np.subtract(raw_utci, 273.15)
    # get daily average, use numpy mean to get the average value across the 24 hours (bands)
    daily_utci_degc = np.mean(utci_degc, axis=0)
    # save daily average to a new tif file, all metadata is from viewing info from raw_data variable
    with rasterio.open(os.path.join(data_dir, os.path.splitext(file)[0]+'_daily_edit.tif'),
                       'w',
                       driver='GTiff',
                       height=daily_utci_degc.shape[0],
                       width=daily_utci_degc.shape[1],
                       count=1,
                       dtype=daily_utci_degc.dtype,
                       nodata=-9.0e33,
                       transform=(0.25, 0.0, -180.125, 0.0, -0.25, 90.125)) as dst:
        dst.write(daily_utci_degc, 1)
    daily_mean_tifs.append(os.path.abspath(os.path.join(data_dir, os.path.splitext(file)[0]+'_daily_edit.tif')))
    print(daily_mean_tifs)


def find_same_month(file_list, target_year, target_month):
    """Utility for finding all files of the same month and year to process
        Params:
            file_list (list): list of files to look through
            target_year (string): year to find files for - YYYY format
            target_month (string): month to find files for - MM format

        Returns: list of file names
    """
    target_month_list = []
    for f in file_list:
        month_match = fnmatch.fnmatch(f, '*_'+target_year+target_month+'*')
        if month_match:
            target_month_list.append(f)
    return target_month_list


# get list of tifs that are in the target year and month
month_list = find_same_month(daily_mean_tifs, target_year='2022', target_month='01')

# TODO calculate the monthly mean from these tifs
# read in monthly tifs using rasterio
daily_mean_arrays_list = []
profiles_list = []
for d in month_list:
    with rasterio.open(d) as src:
        array = src.read()
        profile = src.profile
        daily_mean_arrays_list.append(array)
        profiles_list.append(profile)

# calculate the monthly mean from the daily means
monthly_mean = np.mean(daily_mean_arrays_list, axis=0)

# write the monthly mean to a geotiff file, copying the profile information from one of the original tifs
profile_out = profiles_list[0].copy()
profile_out.update(dtype=monthly_mean.dtype.name)
with rasterio.open(os.path.join(data_dir, '2022_01_monthly_mean.tif'), 'w', **profile_out) as dst:
    dst.write(monthly_mean)

src.close()

# TODO create list of names for processed data files
#processed_data_file = []

