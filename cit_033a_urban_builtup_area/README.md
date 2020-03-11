## Urban Built-up Area Dataset Pre-processing
This file describes the data pre-processing that was done to the [GHS-BUILT dataset](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) for [display on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

The version of the GHS-BUILT dataset that appears on Resource Watch can be retrieved from the [source website](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) by selecting the following parameters from the panel on the left side:
 - **Product**: GHS-BUILT
 - **Epoch**: Multitemporal
 - **Resolution**: 30m
 - **Coord. system**: Mercator

The source provided a global download option for the data, which downloaded a zipped file containing:
1) a single virtual raster (VRT) file with global coverage
2) a series of tif files, each covering a specific region of the world; the tiles collectively have global coverage

The data needed to be in a tif file to upload to Google Earth Engine. Since the VRT file was very large, it could not be converted directly to a tif file using GDAL. Therefore, each of the individual tif tiles had to be uploaded to Google Earth Engine and mosaicked into a global image. 

All the files could not be uploaded to GEE at the same time because their number exceeded the maximum number of assets we could have in GEE. Therefore, the tiles were uploaded and mosaicked in batches. The following steps were taken:

1) Upload a batch of files to a single image collection in GEE.
   - The tif files were uploaded to Google Earth Engine (GEE) with a Python script, rather than through the user interface. Therefore, each file had to be uploaded to a Google Cloud Bucket and then to Google Earth Engine. Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_033a_urban_builtup_area/cit_033a_urban_built_up_area_processing.py) for more details on the upload process.
2) Mosaic the image collection into a single image and save this, using the following code:
```
// Purpose: Mosaic a collection of tif files and export them to an asset


// Mosaic a batch of tif files

//Load in a batch of image collection
var ic = ee.ImageCollection('projects/resource-watch-gee/cit_033a_urban_built_up_area_mosaic');

//Mosaic image collection
var mosaic = ic.mosaic();

//Get projection
var projection = ic.first().projection();
var crs = projection.getInfo().crs;
var transform = projection.getInfo().transform;

//Save global bounds!
var rect = [-180, -89.9, 180, 89.9];
var bounds = ee.Geometry.Rectangle(rect,null,false);

//Export mosaiced image to an asset
Export.image.toAsset({
  image: mosaic,
  description: 'Exporting Urban_built_up_mosaic_number_1',
  // CHANGE THE assetId EVERYTIME YOU MOSAIC A NEW SET OF TILES
  assetId: 'projects/resource-watch-gee/cit_033a_urban_built_up_area_1',
  crs: crs,
  crsTransform: transform,
  region: bounds,
  maxPixels: 1e13
});

// After reapeating this process for all the batches, we ended up with 4 mosaiced images

//////////////////////////////////////////////////////

// Create a final mosaic using the 4 previously mosaiced images to create the final global product

// Load the 4 previously mosaiced images
var image1 = ee.Image("projects/resource-watch-gee/cit_033a_urban_built_up_area_1");
var image2 = ee.Image("projects/resource-watch-gee/cit_033a_urban_built_up_area_2");
var image3 = ee.Image("projects/resource-watch-gee/cit_033a_urban_built_up_area_3");
var image4 = ee.Image("projects/resource-watch-gee/cit_033a_urban_built_up_area_4");


// Create an image collection from the four previously mosaiced images 
var ic = ee.ImageCollection([image1, image2, image3, image4]);
print('collectionFromConstructor: ', ic);

//Mosaic images from image collection
var mosaic = ic.mosaic();

//Get projection
var projection = ic.first().projection();
var crs = projection.getInfo().crs;
var transform = projection.getInfo().transform;

//Save global bounds!
var rect = [-180, -89.9, 180, 89.9];
var bounds = ee.Geometry.Rectangle(rect,null,false);

//Export image 
Export.image.toAsset({
  image: mosaic,
  description: 'Exporting Urban_built_up_final_mosaic',
  assetId: 'projects/resource-watch-gee/cit_033a_urban_built_up_area_30m_mosaic',
  crs: crs,
  crsTransform: transform,
  region: bounds,
  maxPixels: 1e13
});

//Print one image from collection
print(ic.first());
//Print scale in meters at the equator
print(ic.first().projection().nominalScale());
Map.addLayer(mosaic);
```
3) Delete all the images that were used in the mosaic.
4) Repeat steps 1-3 until all tiles had been uploaded and mosaicked in GEE.

Once all of the tiles were uploaded to GEE, a final mosaic with global coverage was made out of each of batches. This final mosaic is what is displayed on Resource Watch. 

You can view the processed Urban Built-up Area dataset [on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
