## Coral Reef Locations Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Distribution of Coral Reefs (2018)](http://data.unep-wcmc.org/datasets/1) for [display on Resource Watch](https://resourcewatch.org/data/explore/1d23838e-40da-4cf3-b61c-56258d3a5c56).

The source provided this dataset as two shapefiles - one of which contains polygon data, and the other contains point data.

Below, we describe the steps used to reformat the shapefile:
1. Read in the polygon shapefile as a geopandas data frame.
2. Change the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integers.
3. Convert the geometries of the data from shapely objects to geojsons.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.

Next, a mask layer was created so that it could be overlayed on top of other datasets to highlight where coral reefs were located. In order to create this, a 10km buffer was generated around each coral reef polygon. This was created and exported as a shapefile in Google Earth Engine, using the following code:

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/bio_004a_coral_reef_locations/bio_004a_coral_reef_locations_processing.py) for more details on this processing.

You can view the processed Coral Reef Locations dataset [on Resource Watch](https://resourcewatch.org/data/explore/1d23838e-40da-4cf3-b61c-56258d3a5c56).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/bio_004a_coral_reef_locations.zip), or [from the source website](http://data.unep-wcmc.org/datasets/1).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
