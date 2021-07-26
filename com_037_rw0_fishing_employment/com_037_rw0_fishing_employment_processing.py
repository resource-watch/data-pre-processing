import logging
import pandas as pd
import numpy as np
import glob
import os
import sys
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import requests
from zipfile import ZipFile
import shutil

# Set up logging
# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers: logger.removeHandler(handler)
logger.setLevel(logging.INFO)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# name of table on Carto where you want to upload data
# using preexisting table for this dataset
dataset_name = 'com_037_rw0_fisheries_and_fleet_employment' #check

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory
The data was provided as two CSVs that must be manually downloaded from the following urls:
- Agriculture; forestry and fishing: 
    https://www.ilo.org/shinyapps/bulkexplorer28/?lang=en&segment=indicator&id=EMP_TEMP_SEX_ECO_NB_A&ref_area=AFG+ALB+DZA+ASM+AGO+AIA+ATG+ARG+ARM+ABW+AUS+AUT+AZE+BHS+BHR+BGD+BRB+BLR+BEL+BLZ+BEN+BMU+BTN+BOL+BIH+BWA+BRA+VGB+BRN+BGR+BFA+BDI+KHM+CMR+CAN+CPV+CYM+TCD+CHL+CHN+COL+COM+COG+COD+COK+CRI+HRV+CUB+CUW+CYP+CZE+CIV+DNK+DJI+DMA+DOM+ECU+EGY+SLV+GNQ+EST+SWZ+ETH+FRO+FLK+FJI+FIN+FRA+PYF+GAB+GMB+GEO+DEU+GHA+GRC+GRL+GRD+GLP+GUM+GTM+GGY+GIN+GUY+HTI+HND+HKG+HUN+ISL+IND+IDN+IRN+IRL+IMN+ISR+ITA+JAM+JPN+JEY+JOR+KAZ+KEN+KIR+KOR+KOS+KWT+KGZ+LAO+LVA+LBN+LSO+LBR+LIE+LTU+LUX+MAC+MDG+MWI+MYS+MDV+MLI+MLT+MHL+MTQ+MRT+MUS+MEX+FSM+MDA+MNG+MNE+MSR+MAR+MOZ+MMR+NAM+NRU+NPL+NLD+ANT+NCL+NZL+NIC+NER+NGA+NIU+MKD+MNP+NOR+PSE+OMN+PAK+PLW+PAN+PNG+PRY+PER+PHL+POL+PRT+PRI+QAT+ROU+RUS+RWA+REU+SHN+KNA+LCA+VCT+WSM+SMR+STP+SAU+SEN+SRB+SYC+SLE+SGP+SVK+SVN+SLB+ZAF+ESP+LKA+SDN+SUR+SWE+CHE+SYR+TWN+TJK+TZA+THA+TLS+TGO+TON+TTO+TUN+TUR+TCA+TUV+UGA+UKR+ARE+GBR+USA+URY+UZB+VUT+VEN+VNM+YEM+ZMB+ZWE&sex=SEX_T+SEX_M+SEX_F+SEX_O&classif1=ECO_ISIC4_A+ECO_ISIC3_A+ECO_ISIC3_B&timefrom=1947&timeto=2020
- ISIC-Rev.4, 2 digit level: 03 & ISIC-Rev.3.1, 2 digit level: 05 (Fishing and aquaculture & ): 
    https://www.ilo.org/shinyapps/bulkexplorer28/?lang=en&segment=indicator&id=EMP_TEMP_SEX_EC2_NB_A&ref_area=AFG+ALB+AGO+ARM+AUT+BGD+BRB+BEL+BOL+BIH+BWA+BRA+BRN+BGR+BFA+BDI+KHM+TCD+CHL+COL+COM+COG+COD+COK+CRI+HRV+CYP+CZE+CIV+DNK+DOM+ECU+EGY+SLV+EST+SWZ+ETH+FJI+FIN+FRA+GMB+GEO+DEU+GHA+GRC+GTM+GUY+HND+HUN+ISL+IND+IDN+IRN+IRL+ISR+ITA+JPN+JOR+KEN+KIR+KOS+KGZ+LAO+LVA+LBN+LSO+LBR+LTU+LUX+MDG+MDV+MLI+MLT+MHL+MRT+MUS+MEX+FSM+MNG+MNE+MSR+MOZ+MMR+NAM+NRU+NPL+NLD+NIC+NER+MKD+NOR+PSE+PAK+PLW+PAN+PNG+PER+PHL+POL+PRT+ROU+RWA+WSM+SRB+SYC+SLE+SVK+SVN+SLB+ESP+LKA+SDN+SUR+SWE+CHE+TJK+TZA+THA+TLS+TGO+TON+TUR+TUV+UGA+ARE+GBR+USA+URY+VUT+VEN+VNM+YEM+ZMB+ZWE&sex=SEX_T+SEX_M+SEX_F+SEX_O&classif1=EC2_ISIC4_A03+EC2_ISIC3_B05&timefrom=1992&timeto=2020

'''

# Create a data dictionary to store the relevant information about each file 
    # raw_data_file: empty list for raw data files (list)
    # processed_dfs: empty list for processed dataframes (list)

data_dict= {
    'raw_data_file': [],
    'processed_dfs': []
  } 
 

# move the data from 'Downloads' into the data directory
source = os.path.join(os.getenv("DOWNLOAD_DIR"),'EMP_TEMP_SEX_*_NB_A-filtered-*.csv')

dest_dir = os.path.abspath(data_dir)
for file in glob.glob(source):
    logger.info(file)
    shutil.copy(file, dest_dir)
    raw_data_file = os.path.join(data_dir, os.path.basename(file))
    data_dict['raw_data_file'].append(raw_data_file)

'''
Process the data 
'''


for file in data_dict['raw_data_file']:
    # read in the data as a pandas dataframe 
    df = pd.read_csv(file,encoding='latin-1')

    # remove '.label' from the end of column headings
    old_columns = list(df.columns)
    df.columns = [column.split('.')[0] for column in old_columns]  
    
    # rename the time and area columns
    df.rename(columns={'time':'year'}, inplace=True)
    df.rename(columns={'ref_area':'area'}, inplace=True)

    # add a suffix to columns that will be duplicated in the merge to indicate the origin dataset
    # create a list of columns that will be duplicated
    column_list= ['source', 'indicator', 'classif1', 'obs_value', 'obs_status', 'note_indicator', 'note_source','note_classif']
    value = df['classif1'][0]
    # append a suffix to the end of the column heading 
    if df['classif1'][0] =='Economic activity (ISIC-Rev.4): A. Agriculture; forestry and fishing':
        for column in column_list:
            df.rename(columns={column: column+'_natural'}, inplace=True)
    elif df['classif1'][0] =='Economic activity (ISIC-Rev.4), 2 digit level: 03 - Fishing and aquaculture':
        for column in column_list:
            df.rename(columns={column: column +'_fish'}, inplace=True)

    # store the processed df
    data_dict['processed_dfs'].append(df)

# join the new and historic datasets
df= pd.merge(data_dict['processed_dfs'][0], data_dict['processed_dfs'][1], how= 'outer', on=['area','year','sex'])

# convert Year column to date time object
df['datetime'] = pd.to_datetime(df.year, format='%Y')


# sort the new data frame by country and year
df= df.sort_values(by=['area','year','sex'])

# reorder the columns
df = df[['area', 'year', 'sex', 'indicator_fish', 'classif1_fish', 'source_fish',
       'obs_value_fish', 'obs_status_fish', 'note_indicator_fish',
       'note_source_fish','indicator_fish', 'classif1_natural', 'source_natural',
       'obs_value_natural', 'obs_status_natural', 'note_classif_natural',
       'note_indicator_natural', 'note_source_natural']]

# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK',tags = ['ow'])

'''
Upload original data and processed data to Amazon S3 storage
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading original data to S3.')
# Copy the raw data into a zipped file to upload to S3
raw_data_dir = os.path.join(data_dir, dataset_name+'.zip')
with ZipFile(raw_data_dir,'w') as zip:
     raw_data_files = data_dict['raw_data_file']
     for raw_data_file in raw_data_files:
        zip.write(raw_data_file, os.path.basename(raw_data_file))
# Upload raw data file to S3
uploaded = util_cloud.aws_upload(raw_data_dir, aws_bucket, s3_prefix+os.path.basename(raw_data_dir))

logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file)) 
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
