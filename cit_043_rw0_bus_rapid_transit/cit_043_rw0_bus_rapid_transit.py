import logging
import pandas as pd
import os
import sys
import dotenv
#insert the location of your .env file here:
dotenv.load_dotenv('/home/hastur_2021/documents/rw_github/cred/.env')
utils_path = os.path.join(os.path.abspath(os.getenv('PROCESSING_DIR')),'utils')
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud
import util_carto
import datetime
from bs4 import BeautifulSoup
import requests
from zipfile import ZipFile
import re

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
dataset_name = 'cit_043_rw0_bus_rapid_transit' #check

# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

logger.info('Executing script for dataset: ' + dataset_name)
# create a new sub-directory within your specified dir called 'data'
# within this directory, create files to store raw and processed data
data_dir = util_files.prep_dirs(dataset_name)

'''
Download data and save to your data directory

Part of this processing was adapted from Kiprono Elijah Koech article:
https://towardsdatascience.com/web-scraping-scraping-table-data-1665b6b2271c
'''

# Retrieve the html page from source
url="https://brtdata.org/indicators/systems/year_system_commenced"
# Make a GET request to fetch the raw HTML content
html_content = requests.get(url).text
# Parse HTML code for the entire site
soup = BeautifulSoup(html_content, "lxml")
# The following line will generate a list of HTML content for the table that we will scrape
gdp = soup.find_all("table")
# Scrape table with HTML code gdp[0]
table = gdp[0]
# the head will form our column names
body = table.find_all("tr")
# Head values (Column names) are the first items of the body list
head = body[0] # 0th item is the header row
body_rows = body[1:] # All other items becomes the rest of the rows
# Declare empty list to keep Columns names
headings = []
for item in head.find_all("th"): # loop through all th elements
    # convert the th elements to text and strip "\n"
    item = (item.text).rstrip("\n")
    # append the clean column name to headings
    headings.append(item)

# Next is now to loop though the rest of the rows

# list to store all rows
all_rows = [] 
# Iterate over the rest of rows from the table
for row_num in range(len(body_rows)): 
    # this list will hold entries for one row
    row = [] 
    # loop through all row entries
    for row_item in body_rows[row_num].find_all("td"): 
        # the following regex is to remove \xa0 and \n and comma from row_item.text
        # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
        aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
        #append aa to row - note one row entry is being appended
        row.append(aa)
    # append one row to all_rows
    all_rows.append(row)

# We can now use the data on all_rows a and headings to create a dataframe
# all_rows becomes our data and headings the column names
df_edit = pd.DataFrame(data=all_rows,columns=headings)
# Drop "Year" column since it is empty
df_edit = df_edit.drop('Year', 1)
# Rename the "Value" column as "Year"
df_edit.rename(columns={'Value':'Year'}, inplace=True)
# convert the column names to lowercase
df_edit.columns = [x.lower() for x in df_edit.columns]
# convert the data type of the column 'year' to integer
df_edit['year'] = df_edit['year'].astype('int64')
# convert the years in the 'year' column to datetime objects and store them in a new column 'datetime'
df_edit['datetime'] = [datetime.datetime(x, 1, 1) for x in df_edit.year]
# replace all NaN with None
df_edit = df_edit.where((pd.notnull(df_edit)), None)
# save processed dataset to csv
processed_data_file = os.path.join(data_dir, dataset_name+'_edit.csv')
df_edit.to_csv(processed_data_file, index=False)

'''
Upload processed data to Carto
'''
logger.info('Uploading processed data to Carto.')
util_carto.upload_to_carto(processed_data_file, 'LINK')

'''
Only upload  processed data to Amazon S3 storage since
we scraped the source's website
'''
# initialize AWS variables
aws_bucket = 'wri-public-data'
s3_prefix = 'resourcewatch/'

logger.info('Uploading processed data to S3.')

# Copy the processed data into a zipped file to upload to S3
processed_data_dir = os.path.join(data_dir, dataset_name+'_edit.zip')
with ZipFile(processed_data_dir,'w') as zip:
    zip.write(processed_data_file, os.path.basename(processed_data_file)) 
        
# Upload processed data file to S3
uploaded = util_cloud.aws_upload(processed_data_dir, aws_bucket, s3_prefix + os.path.basename(processed_data_dir))
