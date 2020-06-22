import os
import sys
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))
import subprocess
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
                  
def merge_geotiffs(tifs, multitif):
    '''
    Merge input single-band geotiffs into one multi-band geotiff
    INPUT   tifs: file names of all single-band geotiffs to merge (list of strings)
            multitif: file name of resulting, multi-band geotiff
    '''
    # merge all the sub tifs from this netcdf to create an overall tif representing all variable
    merge_path = os.path.abspath(os.path.join(os.getenv('GDAL_DIR'),'gdal_merge.py'))
    cmd = '{} "{}" -separate {} -o {}'.format(sys.executable, merge_path, ' '.join(tifs), multitif)
    completed_process = subprocess.run(cmd, shell=False)
    logger.debug(str(completed_process))
    if completed_process.returncode!=0:
        raise Exception('Merging of GeoTiffs using gdal_merge.py failed! Command: '+str(cmd))
    return    
                  