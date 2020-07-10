## Coral Reef Locations Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Distribution of Coral Reefs (2018)](http://data.unep-wcmc.org/datasets/1) for [display on Resource Watch](https://resourcewatch.org/data/explore/6acb7469-29b4-4712-8254-8c130314337b).

The source provided this dataset as two shapefiles - one of which contains polygon data, and the other contains point data.

Below, we describe the steps used to reformat the shapefile to upload it to Carto.
1. Read in the polygon shapefile as a geopandas data frame.
2. Change the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integers.
3. Convert the geometries of the data from shapely objects to geojsons.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/bio_004_coral_reef_locations/bio_004_coral_reef_locations_processing.py) for more details on this processing.

You can view the processed Coral Reef Locations dataset [on Resource Watch](https://resourcewatch.org/data/explore/6acb7469-29b4-4712-8254-8c130314337b).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](http://data.unep-wcmc.org/datasets/1).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
