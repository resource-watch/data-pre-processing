## Coral Reef Locations Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Distribution of Coral Reefs (2010)](http://data.unep-wcmc.org/datasets/1) for [display on Resource Watch](https://resourcewatch.org/data/explore/6acb7469-29b4-4712-8254-8c130314337b).

The source provided the data in a zipped file which contains:
1) a READ ME file
2) a license file
3) a folder containing Metadata
4) a folder containing a map of the data and the paper that describes the project
5) a shapefile for this dataset and another shapefile for a point dataset

Below, we describe the steps used to reformat the shapefile to upload it to Carto.

1. We read in the data as a geopandas data frame.
2. We changed the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integers.
3. We converted the geometries of the data from shapely to geojson.
4. We created a new column from the index of the data frame to use as unique id in Carto.


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/bio_004_coral_reef_locations/bio_004_coral_reef_locations_processing.py) for more details on this processing.

You can view the processed Coral Reef Locations dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](http://data.unep-wcmc.org/datasets/1).

###### Note: This dataset processing was done by [Yujing Wu](https://wrirosscities.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://wrirosscities.org/profile/amelia-snyder).
