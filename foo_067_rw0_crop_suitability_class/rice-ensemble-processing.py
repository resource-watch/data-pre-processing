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

# define calculate ensemble mean
def calculate_ensemble_mean(tif_list, output_tif_name):
    ''' Calculates the ensemble mean from a collection of tif files and save it as a tif file

        Parameters:
            tif_list (list): list of tifs to process
            output_tif_name (string): name for newly generated tif, e.g. 'ensemble_rcp4p5_2020sH_suHg_rcw_edit'

    '''
    # TODO add download steps in here?

    # read in tifs using rasterio
    tif_arrays_list = []
    profiles_list = []
    for t in tif_list:
        with rasterio.open(t) as src:
            array = src.read()
            profile = src.profile
            tif_arrays_list.append(array)
            profiles_list.append(profile)

    # define the mask array as defined in the profile info of the geotifs nodata = -9
    nodata_mask_array = []
    for (tifs, profiles) in zip(tif_arrays_list, profiles_list):
        nd = (tifs == profiles.get('nodata'))
        nodata_mask_array.append(nd)
    '''
    # old way
    # create a nodata mask as defined in the profile info of the geotifs nodata = -9
    # this assumes there are 5 tifs to average
    nodata_mask = np.any((tif_arrays_list[0] == profiles_list[0].get('nodata'),
                          tif_arrays_list[1] == profiles_list[1].get('nodata'),
                          tif_arrays_list[2] == profiles_list[2].get('nodata'),
                          tif_arrays_list[3] == profiles_list[3].get('nodata'),
                          tif_arrays_list[4] == profiles_list[4].get('nodata')),
                         axis=0)
    
    # calculate the mean of all the models to create an ENSEMBLE mean
    # this assumes there are 5 tifs to average
    ensemble_mean = np.mean((tif_arrays_list[0], tif_arrays_list[1], tif_arrays_list[2],
                             tif_arrays_list[3], tif_arrays_list[4]), axis=0)
'''
    # create a nodata mask
    nodata_mask = np.any(nodata_mask_array, axis=0)

    # calculate the mean of all the models to create an ENSEMBLE mean
    ensemble_mean = np.mean(tif_arrays_list, axis=0)

    # replace nodata pixels with np.nan
    ensemble_mean[nodata_mask] = np.nan

    # save ensemble_mean to a tif file
    # Write the ENSEMBLE mean as a geotiff file
    profile_out = profiles_list[0].copy()
    profile_out.update(dtype=ensemble_mean.dtype.name,
                       nodata=np.nan)
    with rasterio.open(os.path.join(data_dir, output_tif_name+'.tif'), 'w', **profile_out) as dst:
        dst.write(ensemble_mean)

    src.close()


'''
Lists of tif URLs to process

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
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHg_rcw.tif'
]
# 2020s, RCP 8.5
rcp8p5_2020sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHg_rcw.tif'
]
# 2050s, RCP 4.5
rcp4p5_2050sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHg_rcw.tif'
]
# 2050s, RCP 8.5
rcp8p5_2050sH_suHg_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHg_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHg_rcw.tif'
]
########################
# wetland rice - rainfed
########################
# 2020s, RCP 4.5
rcp4p5_2020sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHr_rcw.tif'
]
# 2020s, RCP 8.5
rcp8p5_2020sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHr_rcw.tif'
]
# 2050s, RCP 4.5
rcp4p5_2050sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHr_rcw.tif'
]
# 2050s, RCP 8.5
rcp8p5_2050sH_suHr_rcw_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHr_rcw.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHr_rcw.tif'
]
########################
# dryland rice - rainfed
########################
# 2020s, RCP 4.5
rcp4p5_2020sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHr_rcd.tif'
]
# 2020s, RCP 8.5
rcp8p5_2020sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2020sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2020sH/suHr_rcd.tif'
]
# 2050s, RCP 4.5
rcp4p5_2050sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2050sH/suHr_rcd.tif'
]
# 2050s, RCP 8.5
rcp8p5_2050sH_suHr_rcd_list = [
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp8p5/2050sH/suHr_rcd.tif',
    'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp8p5/2050sH/suHr_rcd.tif'
]


'''
Calculate ensemble means from individual model runs for rice.

URLs were obtained from GAEZv4 data portal: https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer 
Under Theme 4: Suitability and Attainable Yield
    Sub-theme: Suitability Index
    Variable name: Suitability index range (0-10000); current cropland in grid cell
'''

# name of dataset
dataset_name = 'foo_067_rw0_crop_suitability_class'

# prep directory for processed tifs
data_dir = util_files.prep_dirs(dataset_name)

# calculate 2020s RCP4.5 for wetland rice
calculate_ensemble_mean(rcp4p5_2020sH_suHg_rcw_list, output_tif_name='ensemble_rcp4p5_2020sH_suHg_rcw_edit')

