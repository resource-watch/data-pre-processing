import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import urllib
import ee
import logging
import time

# set up logging
# get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = 'soc_085_rw1_elevation' #check

logger.info('Executing script for dataset: ' + dataset_name)

'''
Process data
'''
# initialize ee and eeUtil modules for exporting to Google Earth Engine
auth = ee.ServiceAccountCredentials(os.getenv('GEE_SERVICE_ACCOUNT'), os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
ee.Initialize(auth)

# name of the image collection in GEE where the original data is stored  
EE_COLLECTION_ORI = 'JAXA/ALOS/AW3D30/V3_2'

# mosaic the 'DSM' band of the images in the image collection 
mosaicked = ee.ImageCollection(EE_COLLECTION_ORI).select('DSM').mosaic()

# set asset name to be used in GEE
asset_name = f'projects/resource-watch-gee/{dataset_name}'

# create a task to export the mosaiced image to the asset 
task = ee.batch.Export.image.toAsset(image = mosaicked,
                             description = 'export mosaicked image to asset',
                             region = ee.Geometry.Rectangle([-179.999, -90, 180, 90], 'EPSG:4326', False),
                             pyramidingPolicy = {'DSM': 'MEAN'},
                             scale = 30,
                             maxPixels = 1e13,
                             assetId = asset_name)
# start the task
task.start()

'''
# uncomment if you want to check the export task status
# set the state to 'RUNNING' because we have started the task
state = 'RUNNING'
# set a start time to track the time it takes to upload the image
start = time.time()
# wait for task to complete, but quit if it takes more than 21600 seconds
while state == 'RUNNING' and (time.time() - start) < 21600:
    # wait for 20 minutes before checking the state
    time.sleep(1200)
    # check the status of the upload
    status = task.status()['state']
    logging.info('Current Status: ' + status +', run time (min): ' + str((time.time() - start)/60))
    # log if the task is completed and change the state
    if status == 'COMPLETED':
        state = status
        logging.info(status)
    # log an error if the task fails and change the state
    elif status == 'FAILED':
        state = status
        logging.error(task.status()['error_message'])
        logging.debug(task.status())
'''
