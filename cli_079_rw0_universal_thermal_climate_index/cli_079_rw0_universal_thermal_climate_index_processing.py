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
import logging

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'cli_079_rw0_universal_thermal_climate_index'

logger.info('Executing script for dataset: ' + dataset_name)

'''
Download data
'''

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# declare years and months to download data for
# NOTE: data is large -- files for 2021 + 2022 are 13G total and take a long time to download
years = ['2021', '2022']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# access CDS API to download UTCI data; for more info see: https://cds.climate.copernicus.eu/api-how-to
c = cdsapi.Client()
c.retrieve(
    'derived-utci-historical',
    {
        'variable': 'universal_thermal_climate_index',
        'version': '1_1',
        'product_type': 'consolidated_dataset',
        'year': [
            *years,
        ],
        'month': [
            *months,
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
    os.path.join(data_dir, 'utci_download.zip'))

# unzip source data
with ZipFile('data/utci_download.zip', 'r') as zip_obj:
    # create list of raw file names
    raw_file = zip_obj.namelist()
    zip_obj.extractall(data_dir)
    zip_obj.close()

logger.info('Finished downloading data from CDS')

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

# create a list of raw data file names
raw_data_file = [os.path.abspath(os.path.join(data_dir, file)) for file in os.listdir(data_dir) if file.endswith('.nc')]

'''
Process Data
'''

# open netcdf files and calculate daily mean
daily_mean_tifs = []
for file in raw_data_file:
    raw_data = netCDF4.Dataset(file, 'r')
    # isolate the universal thermal climate index (utci) variable
    raw_utci = raw_data.variables['utci'][:]
    # convert from kelvin to celsius (subtract 273.15)
    utci_degc = np.subtract(raw_utci, 273.15)
    # get daily average, use numpy mean to get the average value across the 24 hours (bands)
    daily_utci_degc = np.mean(utci_degc, axis=0)
    # save daily average to a new tif file, all metadata can be found from viewing the raw_data variable
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
    """Utility for matching files of the same month and year to process

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


def calculate_monthly_mean(tif_list, output_directory, output_filename):
    """Utility to calculate the monthly mean from a list of tifs

       Params:
            tif_list (list): list of daily tif files to process
            output_directory (string): directory to save new tif to
            output_filename (string): filename for the newly created tif

       Returns: monthly mean tif file saved to specified directory
    """
    # read in daily mean tifs using rasterio
    daily_mean_arrays_list = []
    profiles_list = []
    for file in tif_list:
        with rasterio.open(file) as src:
            array = src.read()
            profile = src.profile
            daily_mean_arrays_list.append(array)
            profiles_list.append(profile)

    # calculate the monthly mean from the daily mean tifs
    monthly_mean = np.mean(daily_mean_arrays_list, axis=0)

    # write the monthly mean to a geotiff file, copying the profile information from one of the original tif files
    profile_out = profiles_list[0].copy()
    profile_out.update(dtype=monthly_mean.dtype.name)
    with rasterio.open(os.path.join(output_directory, output_filename), 'w', **profile_out) as dst:
        dst.write(monthly_mean)

    src.close()


# calculate monthly mean and save as a new tif file
processed_data_file = []
for year in years:
    print(year)  # check
    for month in months:
        print(month)  # check
        # call function to match all the daily mean tifs together and process by month
        process_month = find_same_month(daily_mean_tifs, year, month)
        print(process_month)  # check
        # call function to calculate the monthly means
        if len(process_month) > 0:
            calculate_monthly_mean(process_month, data_dir, 'monthly_mean_utci_edit_'+year+'_'+month)
        else:
            print('No data for specified time period')

# generate names for the processed tif files
processed_data_file = [mm for mm in os.listdir(data_dir)
                       if fnmatch.fnmatch(mm, 'monthly_mean_utci_edit_*')]

logger.info('Finished processing data')

'''
Upload processed data to Google Earth Engine
'''
