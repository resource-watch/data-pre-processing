## Watersheds that Transport Wastewater to Coastal Ocean Dataset Pre-processing
This file describes the data pre-processing that was done to the [Global Inputs and Impacts from of Human Sewage in Coastal Ecosystems](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258898) for [display on Resource Watch](https://resourcewatch.org/data/explore/784732cc-8e7e-4dac-be51-d4506ff2ee04).

The source provided this dataset as a shapefile containing polygon data.

Below, we describe the steps used to reformat the shapefile to upload it to Carto:

1. Read in the table as a geopandas data frame.
2. Convert the data type of the columns to integer (geometry column excluded).
3. Transform the projection from ESRI 54009 to EPSG 4326.


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_027c_rw0_wastewater_watersheds/ocn_027b_rw0_wastewater_watersheds_processing.py) for more details on this processing.

You can view the processed Watersheds that Transport Wastewater to Coastal Ocean dataset [on Resource Watch](https://resourcewatch.org/data/explore/5bf349ec-3b14-4021-a7d4-fc4b8104bd74).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/raster/ocn_027c_rw0_wastewater_watersheds.zip), or [from the source website](https://knb.ecoinformatics.org/view/urn%3Auuid%3Ac7bdc77e-6c7d-46b6-8bfc-a66491119d07).

###### Note: This dataset processing was done by Claire Hemmerly, and QC'd by [Chris Rowe](https://www.wri.org/profile/chris-rowe).
