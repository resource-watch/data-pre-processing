import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import urllib
from zipfile import ZipFile
import logging
import pandas as pd
import datetime

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
dataset_name = 'cli_049_rw1_dash_pik_historical_emissions' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
'''
# insert the url used to download the data from the source website
url = 'ftp://datapub.gfz-potsdam.de/download/10.5880.PIK.2019.018/PRIMAP-hist_v2.1.zip' #check

# download the data from the source
raw_data_file = os.path.join(data_dir, os.path.basename(url))
urllib.request.urlretrieve(url, raw_data_file)

# unzip source data
raw_data_file_unzipped = raw_data_file.split('.')[0]
zip_ref = ZipFile(raw_data_file, 'r')
zip_ref.extractall(raw_data_file_unzipped)
zip_ref.close()

'''
Process the data 
'''
# read in the data as a pandas dataframe 
df = pd.read_csv(os.path.join(raw_data_file_unzipped, 'PRIMAP-hist_v2.1_09-Nov-2019.csv'))

# subset the dataframe to obtain the aggregated emissions for all countries.
df = df[df.country == 'EARTH']

# subset the dataframe to emissions data of CH4, CO2, F Gases, and N2O 
df = df[df.entity.isin(['CH4', 'CO2', 'FGASESAR4', 'N2O'])]

# subset the dataframe to obtain emissions data that are primarily reported by countries
df = df[df.scenario == 'HISTCR']

# convert the dataframe from wide to long format 
# so there will be one column indicating the year and another column indicating the emissions 
df = df.melt(id_vars = ['scenario', 'country', 'category', 'entity', 'unit'])

# rename the 'variable' and 'value' columns created in the previous step to be 'year' and 'yr_data'
df.rename( columns = { 'variable': 'year', 'value':'yr_data'}, inplace = True)

# convert the emission values of CH4 and N2O to be in the unit of GgCO2eq using global warming potential standards in AR4
df.loc[df.entity == 'CH4', 'yr_data'] = 25 * df.loc[df.entity == 'CH4', 'yr_data']
df.loc[df.entity == 'N2O', 'yr_data'] = 298 * df.loc[df.entity == 'N2O', 'yr_data']

# convert the emission values to be in MtCO2eq
df['yr_data'] = [x * 0.001 for x in df.yr_data]

# change 'GgCO2eq' to be 'MtCO2eq' in the 'unit' column 
df['unit'] = 'MtCO2eq'

# create a dictionary for all the major sectors generating GHG emissions
# the documentation can be found at ftp://datapub.gfz-potsdam.de/download/10.5880.PIK.2019.018/PRIMAP-hist_v2.1_data-description.pdf
category_dict = {'IPCM0EL': 'Total excluding LULUCF',
                 'IPC1': 'Energy',
                 'IPC2': 'Industrial Processes and Product Use',
                 'IPCMAG': 'Agriculture',
                 'IPC4': 'Waste', 
                 'IPC5': 'Other'}

# subset the dataframe to obtain the GHG emissios of major sectors 
df = df[df.category.isin(category_dict.keys())]

# convert the codes in the 'category' column to the sectors they represent
df.category = [category_dict[x] for x in df.category]

# create a 'datetime' column to store the years as datetime objects and drop the 'year' column
df['datetime'] = [datetime.datetime(int(x), 1, 1) for x in df.year]
df.drop(columns = 'year', inplace = True)

# sum the emissions of all types of GHG for each sector in each year
df = df.groupby(['scenario', 'country', 'category', 'unit','datetime']).sum().reset_index()
                 
# create a column 'source' to indicate the data source
df['source'] = 'PIK'

# create a 'gwp' column to indicate that the global warming potential used in the calculation is from IPCC Fourth Assessment Report
df['gwp'] = 'AR4'

# create a 'gas' column to indicate that the emissions values are the sum of all GHG emissions
df['gas'] = 'All GHG'

# rename the 'category' column to 'sector'
df.rename(columns = {'category' : 'sector'}, inplace = True)

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK')

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Upload raw data file to S3

# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
    zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')
# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file))
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix+os.path.basename(processed_data_dir))
