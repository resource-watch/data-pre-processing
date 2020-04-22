import geopandas as gpd
import os
import numpy as np
import glob
import cartosql
import os
import logging
import sys
from collections import OrderedDict
import datetime
import cartosql
import requests
import simplejson
import time

#The purpose of this python code is to upload data from Global Mangrove Watch into the Resource Watch Carto account
#Global Mangrove Watch (GMW) provides version 2 of its data available from this website https://data.unep-wcmc.org/datasets/45 by clicking the "Download" button
#GMW provides a separate shapefile containing the mangrove extents for each year for 1996, 2007, 2008, 2009, 2010, 2015, and 2016
#This code uploads the data from each shapefile into one table in the Resource Watch Carto account
#We also overwrite the unique ID fields of the GMW data in order to provide continuous unique ID's in the carto table


def convert_geometry(geometries):
    '''
    Function to convert shapely geometries to geojsons
    '''
    output = []
    for geom in geometries:
        output.append(geom.__geo_interface__)
    return output

#Table name in carto
table = 'for_005a_mangrove_edit'

#Table structure in carto
CARTO_SCHEMA = OrderedDict([
    ('cartodb_id', 'numeric'),
    ('pxlval', 'numeric'),
    ('year', 'numeric'),
    ('the_geom', 'geometry')
])

#Set data directory. Code is set to run if this python file is copied into the uncompressed data package downloaded from GMW's page https://data.unep-wcmc.org/datasets/45
data_directory = os.path.join(os.getcwd(),'CartoData')
print(data_directory)

#Load in the shapefiles, ordered alphabeticly 
shape_files = sorted(glob.glob(os.path.join(data_directory,'*.shp')))


#The unique ID's for each year is 1,2,3... which results in duplicate unique ID's when the shapefiles are combined
#Therefore we create new unique ID's by adding the last unique ID to next year's unique ID's

#Tracking variable for the cumulative unique ID
index_buffer = 0

#Read in each shapefile in a for loop
for shape_file in shape_files:
    print(shape_file)
    #Read shapefile into geodatabase
    gdf = gpd.read_file(shape_file)
    
    #Add year column, pulled from the filename
    year = os.path.basename(shape_file)
    year = int(year[4:8])
    gdf['Year'] = year
    
    #Order columns
    df = gdf[['ogc_fid','pxlval','Year']]
    
    #Convert old unique ID to new unique ID
    df['ogc_fid'] = np.arange(1,len(df)+1)+index_buffer
    #Save the last unique ID to the tracking variable
    index_buffer = df['ogc_fid'].values[-1]
    
    #Convert shapely geometry to geojson
    df['geometry'] = convert_geometry(gdf['geometry'])
    print(index_buffer)
    
    #Convert geodatabase into json
    new_rows = df.values.tolist()
    print('Inserting new rows for shapefile: {}'.format(shape_file))
    
    #Upload to carto
    cartosql.insertRows(table, CARTO_SCHEMA.keys(),CARTO_SCHEMA.values(), new_rows)
