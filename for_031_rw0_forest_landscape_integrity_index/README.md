## Forest Landscape Integrity Index Dataset Pre-processing
This file describes the data pre-processing that was done to the [Forest Landscape Integrity Index](https://www.forestintegrity.com/) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is provided by the source as a (zipped) GeoTIFF file. The following variables are shown on Resource Watch:
- 2019 Forest Landscape Integrity Index (flii): Continuous index representing the degree of forest anthropogenic modification for the beginning of 2019 
 
The data source multiplied the data by 1000 to store values in Integer format. Data was divided by 1000 in Google Earth Engine to obtain proper values (Range 0-10) for display on RW.

``` javascript
// Purpose: Divide values for the flii band by 1000.

// Scale the flii down by a factor of 1000
var for_031_scaled = for_031.divide(1000)

// Define the visualization parameters
var vizParams= { 
  min: 0,
  max: 10,
  palette: ['6f5817','348303']
}

// Visualize the data
Map.addLayer(for_031_scaled, vizParams,'flii')

// Export the image to an Earth Engine asset.
Export.image.toAsset({
   image: for_031_scaled,
   description: 'forest_landscape_integrity_index_scaled',
   assetId: 'projects/resource-watch-gee/for_031_rw0_forest_landscape_integrity_index_scaled',
   scale: 300,
   maxPixels: 1e13,
   pyramidingPolicy: {
     'flii': 'mean',
   }
 });
```

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_031_rw0_forest_landscape_integrity_index/for_031_rw0_forest_landscape_integrity_index_processing.py) and the [Google Earth Engine script](https://code.earthengine.google.com/61eeab78e3497a64e24b1f50ff685301) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original dataset [from the source website](https://www.forestintegrity.com/download-data).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms) and QC'd by []().