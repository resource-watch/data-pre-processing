## Coral Reef Locations Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Distribution of Coral Reefs (2018)](http://data.unep-wcmc.org/datasets/1) for [display on Resource Watch](https://resourcewatch.org/data/explore/1d23838e-40da-4cf3-b61c-56258d3a5c56).

The source provided this dataset as two shapefiles - one of which contains polygon data, and the other contains point data.

Below, we describe the steps used to reformat the shapefile and create a mask for it.
1. Read in the polygon shapefile as a geopandas data frame.
2. Change the data type of column 'PROTECT', 'PROTECT_FE', and 'METADATA_I' to integers.
3. Convert the geometries of the data from shapely objects to geojsons.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.
5. Create a 10km buffer around each coral reef polygon and export the product as a shapefile in Google Earth Engine.
```
var coral_reefs = ee.FeatureCollection('projects/resource-watch-gee/bio_004a_coral_reef_locations_edit')
var buffer_coral = function(coral) {
  return coral.buffer(10000)
}
var buffered_coral_reefs = coral_reefs.map(buffer_coral)
Export.table.toDrive({
  collection: buffered_coral_reefs,
  description:'bio_004a_coral_reef_locations_buffer',
  fileFormat: 'SHP'
});
```
6. Download the buffer shapefile and read in the data as a geopandas data frame.
7. Create a new field called 'dissolve_id' in the data frame and fill it with 1s.
8. Dissolve all the polygons in the data frame into a single polygon.
9. Remove columns other than the 'geometry' column and reset the index of the data frame.
10. Create a polygon whose extent is the whole world and convert it to a geopandas data frame.
11. Create a mask by finding the difference between the world polygon and the buffered coral reef polygon.
12. Assign the right headers to the columns in the mask data frame.
13. Convert the data type of the column 'cartodb_id' in the mask data frame to integer.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/bio_004a_coral_reef_locations/bio_004a_coral_reef_locations_processing.py) for more details on this processing.

You can view the processed Coral Reef Locations dataset [on Resource Watch](https://resourcewatch.org/data/explore/1d23838e-40da-4cf3-b61c-56258d3a5c56).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/bio_004a_coral_reef_locations.zip), or [from the source website](http://data.unep-wcmc.org/datasets/1).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
