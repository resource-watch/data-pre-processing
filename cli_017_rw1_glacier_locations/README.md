## {Resource Watch Public Title} Dataset Pre-processing
This file describes the data pre-processing that was done to [the Glacier Locations](http://glims.colorado.edu/glacierdata/) for [display on Resource Watch](put in the link for the new RW dataset).

The source provided the dataset as two shapefiles in a zipped folder. 

1. Glims Glacier Locations (points)
2. Glims Glaceir Extent (polygons)

Below, we describe the steps used to reformat the shapefiles to upload to Carto.

1. Import the shapefiles as geopandas dataframes.
2. Rename columns to match the current version of Carto table.


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/master/cli_017_rw2_glacier_locations/cli_017_rw2_glacier_locations_processing.py) for more details on this processing.

You can view the processed Glacier Locations dataset [on Resource Watch](link to new dataset).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/cli_017_glacier_extent.zip), or [from the source website](http://www.glims.org/download/).

###### Note: This dataset processing was done by [Jason Winik](https://www.wri.org/profile/jason-winik), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
