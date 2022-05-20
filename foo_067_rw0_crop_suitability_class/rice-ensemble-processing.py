import numpy as np
import rasterio
import os
import urllib.request
from urllib.parse import urlsplit
import re
import sys


# script to process the individual model outputs from GAEZv4 Suitability Index tifs and compute ENSEMBLE mean tifs

# rough outline of processing steps

# tifs to process
# 2020s wetland rice
NorESM1_M = 'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/NorESM1-M/rcp4p5/2020sH/suHg_rcw.tif'
MIROC_ESM_CHEM = 'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/MIROC-ESM-CHEM/rcp4p5/2020sH/suHg_rcw.tif'
IPSL_CM5A_LR = 'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/IPSL-CM5A-LR/rcp4p5/2020sH/suHg_rcw.tif'
HadGEM2_ES = 'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/HadGEM2-ES/rcp4p5/2020sH/suHg_rcw.tif'
GFDL_ESM2M = 'https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/res05/GFDL-ESM2M/rcp4p5/2020sH/suHg_rcw.tif'

# read in tifs
with rasterio.open(NorESM1_M) as src:
    nor_array = src.read()
    nor_profile = src.profile
with rasterio.open(MIROC_ESM_CHEM) as src:
    mir_array = src.read()
    mir_profile = src.profile
with rasterio.open(IPSL_CM5A_LR) as src:
    ips_array = src.read()
    ips_profile = src.profile
with rasterio.open(HadGEM2_ES) as src:
    had_array = src.read()
    had_profile = src.profile
with rasterio.open(GFDL_ESM2M) as src:
    gfd_array = src.read()
    gfd_profile = src.profile

# create a nodata mask as defined in the profile info of the geotifs nodata = -9
nodata_mask = np.any((nor_array == nor_profile.get('nodata'),
                      mir_array == mir_profile.get('nodata'),
                      ips_array == ips_profile.get('nodata'),
                      had_array == had_profile.get('nodata'),
                      gfd_array == gfd_profile.get('nodata')),
                      axis=0)

# calculate the mean of all the models to create an ENSEMBLE mean
ensemble_mean = np.mean((nor_array, mir_array, ips_array, had_array, gfd_array), axis=0)

# replace nodata pixels with np.nan
ensemble_mean[nodata_mask] = np.nan

# write the ENSEMBLE mean array to a geotiff file
profile_out = nor_profile.copy()
profile_out.update(dtype=ensemble_mean.dtype.name,
                   nodata=np.nan)
with rasterio.open('/Users/alexsweeney/Desktop/test/test-ensemble-mean.tif', 'w', **profile_out) as dst:
    dst.write(ensemble_mean)