import os
import subprocess
import glob
from shutil import copy


DATA_DIR = 'C:\\Users\\taufiq.rashid\\OneDrive - World Resources Institute\\Documents\\resource_watch\\1-21\\GHS_BUILT_LDSMT_GLOBE_R2018A_3857_30_V2_0\\V2-0\\30x150000\\'
DEST_DIR = 'C:\\Users\\taufiq.rashid\\OneDrive - World Resources Institute\\Documents\\resource_watch\\1-21\\GHS_BUILT_LDSMT_GLOBE_R2018A_3857_30_V2_0\\V2-0\\temp\\'
GS_BUCKET = 'gs://rw-gee/temp/'

os.chdir(DATA_DIR)
PAUSE_FOR_OVERLOAD = True
NUM_ASSETS_AT_ONCE = 50


# Get the list of all individual tif files
files = glob.glob(DATA_DIR + '\\**\\*.tif', recursive = True)
#Create empty array for task id's
task_ids = ['']*len(files)

print(len(files))


for i,filey in enumerate(files):		

    # Rename all files to include extension at the end to avoid overwritting of duplicate names
    filename = filey.split('.tif')[0]+'_{}.tif'.format(i)
	os.rename(filey,filename)

    # copy all files to a single directory to use parallel upload
	copy(filey, DEST_DIR)
    	  

# Transfer all files to the Google Cloud Bucket
cmd = ['gsutil','-m','cp','-r',DEST_DIR,GS_BUCKET]
subprocess.call(cmd, shell=True)  

# Transfer files from Bucket to GEE

EE_COLLECTION = 'projects/resource-watch-gee/cit_033a_urban_built_up_area_mosaic'


def upload_asset(full_file_path, DATA_DIR=DATA_DIR, EE_COLLECTION=EE_COLLECTION, GS_BUCKET=GS_BUCKET):
    '''
    Function to upload geotiffs as images
    '''
    
    filename = os.path.basename(full_file_path)

    #Get asset id
    asset_id = EE_COLLECTION+'/'+filename.split('.')[0]

    #Upload GeoTIFF from google storage bucket to earth engine
    cmd = ['earthengine','upload','image','--asset_id='+asset_id,'--force',GS_BUCKET+'/'+filename]

    shell_output = subprocess.check_output(cmd, shell=True)
    shell_output = shell_output.decode("utf-8")
    print(shell_output)

    #Get task id
    task_id = ''
    if 'Started upload task with ID' in shell_output:
        task_id = shell_output.split(': ')[1]
        task_id = task_id.strip()
    else:
        print('Something went wrong!')
        task_id='ERROR'
    return task_id

# Loop through each indivual tiles to upload them to Google Earth Engine
for i,filey in enumerate(files):
    print(i)

    if i >=0 and i <= 5000: # repeat this process for len(files)
    
        task_id = upload_asset(filey)
        
        if PAUSE_FOR_OVERLOAD:
            if (i% NUM_ASSETS_AT_ONCE == 0) and (i>0):
                #Wait for all tasks to finish
                cmd = ['earthengine','task','wait','all']
                subprocess.call(cmd, shell=True)