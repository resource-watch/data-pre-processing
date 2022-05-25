import numpy as np
import rasterio
import os
import sys
from dotenv import load_dotenv
load_dotenv()
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')), 'utils')
if utils_path not in sys.path:
   sys.path.append(utils_path)
import util_files
import urllib.request
from urllib.parse import urlsplit
import re

# script to process the individual model outputs from GAEZv4 Suitability Index tifs and compute ENSEMBLE mean tifs

# define dataset name
dataset_name = 'foo_067_rw0_crop_suitability_class'

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

# define calculate ensemble mean
def calculate_ensemble_mean(tif_list, output_tif_name):
    ''' Calculates the ensemble mean from a collection of tif files and save it as a tif file

        Parameters:
            tif_list (list): list of tifs to process
            output_tif_name (string): name for newly generated tif, e.g. 'ensemble_rcp4p5_2020sH_suHg_rcw_edit'

    '''
    # prep directory to store raw individual model data
    # create a new sub-directory within your specified data dir called 'raw_model_data' to store files
    raw_data_dir = os.path.join(data_dir, 'raw_model_data')
    if not os.path.exists(raw_data_dir):
        os.mkdir(raw_data_dir)

    # download tifs into raw data directory, and retain unique path information contained in URLs to use as filename
    raw_data_file = []
    for url in tif_list:
        # split URL to access path info
        s = urlsplit(url)
        # swap "/" for "-" in the path
        r = re.sub("/", "-", s.path)
        # remove the beginning portion of path which is common to all urls
        p = r.replace("-data.gaezdev.aws.fao.org-res05-", "")
        # create a new path and filename
        filename = os.path.join(raw_data_dir, p)
        # download data and save with new filename in data_dir
        d = urllib.request.urlretrieve(url, filename)
        raw_data_file.append(d[0])

    # read in tifs using rasterio
    tif_arrays_list = []
    profiles_list = []
    for file in raw_data_file:
        with rasterio.open(file) as src:
            array = src.read()
            profile = src.profile
            tif_arrays_list.append(array)
            profiles_list.append(profile)

    # define the mask array as defined in the profile info of the raster: nodata = -9
    nodata_mask_array = []
    for (tifs, profiles) in zip(tif_arrays_list, profiles_list):
        nd = (tifs == profiles.get('nodata'))
        nodata_mask_array.append(nd)

    # create a nodata mask
    nodata_mask = np.any(nodata_mask_array, axis=0)

    # calculate the mean of all the models to create an ENSEMBLE mean
    ensemble_mean = np.mean(tif_arrays_list, axis=0)

    # replace nodata pixels with np.nan
    ensemble_mean[nodata_mask] = np.nan

    # write the ENSEMBLE mean to a geotiff file
    profile_out = profiles_list[0].copy()
    profile_out.update(dtype=ensemble_mean.dtype.name,
                       nodata=np.nan)
    with rasterio.open(os.path.join(data_dir, output_tif_name+'.tif'), 'w', **profile_out) as dst:
        dst.write(ensemble_mean)

    src.close()

    return raw_data_file


'''
Process data

Calculate ensemble means from individual model runs for wetland and drylan rice.
URLs were obtained from GAEZv4 data portal: https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer 
Under Theme 4: Suitability and Attainable Yield
    Sub-theme: Suitability Index
    Variable name: Suitability index range (0-10000); current cropland in grid cell
'''

########################
# wetland rice - gravity irrigation
########################
# 2020s, RCP4.5
rcp4p5_2020sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHg_rcw.tif']

# calculate ensemble mean: 2020s RCP4.5 for wetland rice - gravity irrigation
calculate_ensemble_mean(rcp4p5_2020sH_suHg_rcw_list, output_tif_name='ENSEMBLE_rcp4p5_2020sH_suHg_rcw_edit')

# 2020s, RCP 8.5
rcp8p5_2020sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHg_rcw.tif']

# calculate ensemble mean: 2020s RCP8.5 for wetland rice - gravity irrigation
calculate_ensemble_mean(rcp8p5_2020sH_suHg_rcw_list, output_tif_name='ENSEMBLE_rcp8p5_2020sH_suHg_rcw_edit')

# 2050s, RCP 4.5
rcp4p5_2050sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHg_rcw.tif']

# calculate ensemble mean: 2050s RCP4.5 for wetland rice - gravity irrigation
calculate_ensemble_mean(rcp4p5_2050sH_suHg_rcw_list, output_tif_name='ENSEMBLE_rcp4p5_2050sH_suHg_rcw_edit')

# 2050s, RCP 8.5
rcp8p5_2050sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHg_rcw.tif']

# calculate ensemble mean: 2050s RCP8.5 for wetland rice - gravity irrigation
calculate_ensemble_mean(rcp8p5_2050sH_suHg_rcw_list, output_tif_name='ENSEMBLE_rcp8p5_2050sH_suHg_rcw_edit')

########################
# wetland rice - rainfed
########################
# 2020s, RCP 4.5
rcp4p5_2020sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHr_rcw.tif']

# calculate ensemble mean: 2020s RCP4.5 for wetland rice - rainfed
calculate_ensemble_mean(rcp4p5_2020sH_suHr_rcw_list, output_tif_name='ENSEMBLE_rcp4p5_2020sH_suHr_rcw_edit')

# 2020s, RCP 8.5
rcp8p5_2020sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHr_rcw.tif']

# calculate ensemble mean: 2020s RCP8.5 for wetland rice - rainfed
calculate_ensemble_mean(rcp8p5_2020sH_suHr_rcw_list, output_tif_name='ENSEMBLE_rcp8p5_2020sH_suHr_rcw_edit')

# 2050s, RCP 4.5
rcp4p5_2050sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHr_rcw.tif']

# calculate ensemble mean: 2050s RCP4.5 for wetland rice - rainfed
calculate_ensemble_mean(rcp4p5_2050sH_suHr_rcw_list, output_tif_name='ENSEMBLE_rcp4p5_2050sH_suHr_rcw_edit')

# 2050s, RCP 8.5
rcp8p5_2050sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHr_rcw.tif']

# calculate ensemble mean: 2050s RCP8.5 for wetland rice - rainfed
calculate_ensemble_mean(rcp8p5_2050sH_suHr_rcw_list, output_tif_name='ENSEMBLE_rcp8p5_2050sH_suHr_rcw_edit')

########################
# dryland rice - rainfed
########################
# 2020s, RCP 4.5
rcp4p5_2020sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHr_rcd.tif']

# calculate ensemble mean: 2020s RCP4.5 for dryland rice - rainfed
calculate_ensemble_mean(rcp4p5_2020sH_suHr_rcd_list, output_tif_name='ENSEMBLE_rcp4p5_2020sH_suHr_rcd_edit')

# 2020s, RCP 8.5
rcp8p5_2020sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHr_rcd.tif']

# calculate ensemble mean: 2020s RCP8.5 for dryland rice - rainfed
calculate_ensemble_mean(rcp8p5_2020sH_suHr_rcd_list, output_tif_name='ENSEMBLE_rcp8p5_2020sH_suHr_rcd_edit')

# 2050s, RCP 4.5
rcp4p5_2050sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHr_rcd.tif']

# calculate ensemble mean: 2050s RCP4.5 for dryland rice - rainfed
calculate_ensemble_mean(rcp4p5_2050sH_suHr_rcd_list, output_tif_name='ENSEMBLE_rcp4p5_2050sH_suHr_rcd_edit')

# 2050s, RCP 8.5
rcp8p5_2050sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHr_rcd.tif']

# calculate ensemble mean: 2050s RCP8.5 for dryland rice - rainfed
calculate_ensemble_mean(rcp8p5_2050sH_suHr_rcd_list, output_tif_name='ENSEMBLE_rcp8p5_2050sH_suHr_rcd_edit')
