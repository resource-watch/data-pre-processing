import os
import sys
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))
import subprocess
import gdal
import numpy as np
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prep_dirs(dataset_name):
    '''
    Sets working directory for processing dataset, and creates needed directories as necessary
    INPUT   dataset_name: full name of dataset to be processed
    RETURN  data_dir: relative path of directory for holding downloaded and processed data
    '''
    # first, set the directory that you are working in with the path variable
    path = os.path.abspath(os.path.join(os.getenv('PROCESSING_DIR'),dataset_name))
    if not os.path.exists(path):
        os.mkdir(path)
    #move to this directory
    os.chdir(path)
    logger.debug('Working directory absolute path: '+path)
    
    # create a new sub-directory within your specified dir called 'data'
    # within this directory, create files to store raw and processed data
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    return data_dir

def convert_netcdf(nc, subdatasets):
    '''
    Convert netcdf files to geotifs
    INPUT   nc: file name of netcdf to convert (string)
            subdatasets: subdataset names to extract to individual geotiffs (list of strings)
    RETURN  tifs: file names of generated geotiffs (list of strings)
    '''
    # create an empty list to store the names of the tifs we generate from this netcdf file
    tifs = []
    # go through each variables to process in this netcdf file
    for sds in subdatasets:
        # extract subdataset by name
        # should be of the format 'NETCDF:"filename.nc":variable'
        sds_path = f'NETCDF:"{nc}":{sds}'
        # generate a name to save the tif file we will translate the netcdf file's subdataset into
        sds_tif = '{}_{}.tif'.format(os.path.splitext(nc)[0], sds_path.split(':')[-1])
        # translate the netcdf file's subdataset into a tif
        cmd = ['gdal_translate','-q', '-a_srs', 'EPSG:4326', sds_path, sds_tif]
        completed_process = subprocess.run(cmd, shell=False)
        logger.debug(str(completed_process))
        if completed_process.returncode!=0:
            raise Exception('NetCDF conversion using gdal_translate failed! Command: '+str(cmd))
        # add the new subdataset tif files to the list of tifs generated from this netcdf file
        tifs.append(sds_tif)
    return tifs

def mask_geotiff(target, mask, maskedtif, nodata=-128):
    '''
    Apply mask geotiff to target, ie reassign all target pixels outside of mask to specific value.
    Target pixels within mask remain unchanged.
    INPUT   target: file name of (single-band) geotiff to be masked (string)
            mask: file name of (single-band) mask geotiff, ie a binary raster (string)
            maskedtif: file name of masked geotiff (string)
            nodata: value to be written over existing target pixels outside of mask (int/float)
    '''
    calc_path = os.path.abspath(os.path.join(os.getenv('GDAL_DIR'),'gdal_calc.py'))
    cmd = '{} "{}" -A {} -B {} --outfile={} --calc="((B==0)*{})+((B==1)*A)"'.format(sys.executable, calc_path, target, mask, maskedtif, nodata)
#     cmd = '"{calc_path}" -A {target} -B {mask} --outfile={maskedtif} --calc="((B==0)*{nodata})+((B==1)*A)"'
#     logger.debug('Mask GeoTiff command: '+cmd)
    completed_process = subprocess.run(cmd, shell=False)
    logger.debug(str(completed_process))
    if completed_process.returncode!=0:
        raise Exception('Masking of GeoTiff using gdal_calc.py failed! Command: '+str(cmd))
#     instead using command line escape
#     !gdal_calc.py -A {annual} -B {mask} --outfile={annual_masked} --calc="((B==0)*{nodata})+((B==1)*A)"
    return    
                  
def merge_geotiffs(tifs, multitif, ot=None, nodata=None):
    '''
    Merge input single-band geotiffs into one multi-band geotiff. This is a "dumb" merge; for example,
    it destroys all band metadata.
    INPUT   tifs: file names of all single-band geotiffs to merge (list of strings)
            multitif: file name of resulting, multi-band geotiff
    '''
    # merge all the sub tifs from this netcdf to create an overall tif representing all variable
    merge_path = os.path.abspath(os.path.join(os.getenv('GDAL_DIR'),'gdal_merge.py'))
    cmd = '{} "{}" '
    if ot is not None:
        cmd += '-ot {} '.format(ot)
    if no_data is not None:
        cmd += '-a_nodata {} '.format(nodata)
    cmd += '-o {} -separate {} '
    cmd = cmd.format(sys.executable, merge_path, multitif, ' '.join(tifs), )
    completed_process = subprocess.run(cmd, shell=False)
    logger.debug(str(completed_process))
    if completed_process.returncode!=0:
        raise Exception('Merging of GeoTiffs using gdal_merge.py failed! Command: '+str(cmd))
    return
              
def scale_geotiff(tif, scaledtif=None, scale_factor=None, nodata=None, gdal_type=gdal.GDT_Float32):
    '''
    Apply scale factor to geotiff, writing the result to a new geotiff file. 
    Raster values and linked metadata are changed; all other metadata are preserved.
    This function's complexity comes from metadata preservation, and is written with an eye
    towards typical NetCDF metadata contents and structure. If these elements are not relevant,
    then gdal_edit.py or gdal_calc.py may be a simpler solution.
    INPUT   tif: file name of single-band geotiff to be scaled (string)
            scaledtif: file name of output raster; if None, input file name is appended (string)
            scale_factor: scale factor to be applied; if None, value is drawn from metadata (numeric)
            nodata: value to indicate no data in output raster; if None, original value is used (numeric)
            gdal_type: GDAL numeric type of the output raster (gdalconst(int))
    RETURN scaledtif: filename of scaled output raster (string)
    '''
    geotiff = gdal.Open(tif, gdal.gdalconst.GA_ReadOnly)
    assert (geotiff.RasterCount == 1)
    band = geotiff.GetRasterBand(1)
    
    # read in raster
    raster = np.array(band.ReadAsArray())    
    
    # retrieve nodata/fill from band metadata
    # identify nodata entries in raster
    nodata_mask = (raster == band.GetNoDataValue())
    
    # retrieve scale factor from band metadata
    band_metadata = band.GetMetadata()
    band_scale_keys = [key for key, val in band_metadata.items() if 'scale' in key.lower()]
    assert (len(band_scale_keys)<=1)
    band_fill_keys = [key for key, val in band_metadata.items() if 'fill' in key.lower()]
    assert (len(band_fill_keys)<=1)
    assert (float(band_metadata[band_fill_keys[0]])==band.GetNoDataValue())
    if scale_factor is None:
        scale_factor = float(band_metadata[band_scale_keys[0]])
    
    # apply scale factor to raster
    logger.debug(f'Applying scale factor of {scale_factor} to raster of GeoTiff {os.path.basename(tif)}')
    new_raster = raster * scale_factor
    
    # apply nodata fill as desired
    if nodata is None:
        nodata = band.GetNoDataValue()
    new_raster[nodata_mask] = nodata
    
    # update band metadata
    new_band_metadata = band_metadata.copy()
    if len(band_scale_keys) > 0:
        new_band_metadata[band_scale_keys[0]] = str(1)
    if len(band_fill_keys) > 0:
        new_band_metadata[band_fill_keys[0]] = str(nodata)
    if 'valid_max' in new_band_metadata:
        new_band_metadata['valid_max'] = str(float(band_metadata['valid_max']) * scale_factor)
    if 'valid_min' in new_band_metadata:
        new_band_metadata['valid_min'] = str(float(band_metadata['valid_min']) * scale_factor)
    
    # update geotiff metadata
    ds_metadata = geotiff.GetMetadata()
    ds_scale_keys = [key for key, val in ds_metadata.items() if 'scale' in key.lower()]
    assert (len(ds_scale_keys)<=1)
    metadata_band_prefix = ds_scale_keys[0].split('#')[0]
    ds_fill_keys = [key for key, val in ds_metadata.items() if 'fill' in key.lower()]
    assert (len(ds_fill_keys)<=1)
    ds_valid_min_keys = [key for key, val in ds_metadata.items() if metadata_band_prefix.lower()+'#'+'valid_min' in key.lower()]
    assert (len(ds_valid_min_keys)<=1)
    ds_valid_max_keys = [key for key, val in ds_metadata.items() if metadata_band_prefix.lower()+'#'+'valid_max' in key.lower()]
    assert (len(ds_valid_max_keys)<=1)
    
    new_ds_metadata = ds_metadata.copy()
    if len(ds_scale_keys) > 0:
        new_ds_metadata[ds_scale_keys[0]] = str(1)
    if len(ds_fill_keys) > 0:
        new_ds_metadata[ds_fill_keys[0]] = str(nodata)
    if len(ds_valid_min_keys) > 0:
        new_ds_metadata[ds_valid_min_keys[0]] = str(float(ds_metadata[ds_valid_min_keys[0]]) * scale_factor)
    if len(ds_valid_max_keys) > 0:
        new_ds_metadata[ds_valid_max_keys[0]] = str(float(ds_metadata[ds_valid_max_keys[0]]) * scale_factor)
    
    # create output dataset
    # get output file name
    if scaledtif is None:
        dotindex = tif.rindex('.')
        scaledtif = tif[:dotindex] + '_scaled' + tif[dotindex:]
    [cols, rows] = raster.shape
    driver = gdal.GetDriverByName("GTiff")
    outds = driver.Create(scaledtif, rows, cols, 1, gdal_type)
    outds.SetGeoTransform(geotiff.GetGeoTransform())
    outds.SetProjection(geotiff.GetProjection())
    outds.GetRasterBand(1).WriteArray(new_raster)
    outds.GetRasterBand(1).SetMetadata(new_band_metadata)
    outds.GetRasterBand(1).SetNoDataValue(nodata)
    outds.SetMetadata(new_ds_metadata)
    outds.FlushCache()
    outds = None
    band = None
    geotiff = None
    
    return scaledtif  
            
