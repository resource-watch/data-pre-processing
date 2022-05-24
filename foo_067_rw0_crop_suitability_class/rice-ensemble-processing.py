import numpy as np
import rasterio
import os
import urllib.request
from urllib.parse import urlsplit
import re
import sys


# script to process the individual model outputs from GAEZv4 Suitability Index tifs and compute ENSEMBLE mean tifs

# rough outline of processing steps
def calculate_ensemble_mean(tif_list):
    '''
    Calculate the ensemble mean from a collection of tif files
    Return a newly created tif that is the ensemble mean of the 5 input tifs
    '''
    # read in tifs using rasterio
    tif_arrays_list = []
    profiles_list = []
    for t in tif_list:
        with rasterio.open(t) as src:
            array = src.read()
            profile = src.profile
            tif_arrays_list.append(array)
            profiles_list.append(profile)

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

    # replace nodata pixels with np.nan
    ensemble_mean[nodata_mask] = np.nan

    # save ensemble_mean to a tif file
    # Write the ENSEMBLE mean as a geotiff file
    profile_out = profiles_list[0].copy()
    profile_out.update(dtype=ensemble_mean.dtype.name,
                       nodata=np.nan)
    # TODO change output directory and make it dynamic (e.g. use tif list to inform output file name)
    with rasterio.open('/Users/alexsweeney/Desktop/test/test-fnc-ensemble-mean.tif', 'w', **profile_out) as dst:
        dst.write(ensemble_mean)

    src.close()

# calculate ensemble mean of wetland rice 2020s, RCP 4.5

# define tifs to process
# 2020s wetland rice, RCP4.5
rcw_2020s_rcp45_list = ['https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHg_rcw.tif',
'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHg_rcw.tif',
'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHg_rcw.tif',
'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHg_rcw.tif',
'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHg_rcw.tif']

calculate_ensemble_mean(rcw_2020s_rcp45_list)
