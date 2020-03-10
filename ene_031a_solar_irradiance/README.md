## Solar Irradiance Retrieval and Pre-processing
This file describes the process used to retrieve and pre-process the [Global Solar Atlas Version 2 dataset](https://globalsolaratlas.info/download/world) for [display on Resource Watch](https://resourcewatch.org/data/explore/Solar-Irradiance).

Two datasets were downloaded and pre-processed: 1) average daily global horizontal irradiance (9 arcsec resolution), and 2) average daily photovoltaic power potential (30 arcsec resolution).

##### Average daily global horizontal irradiance (9 arcsec resolution)
1) go to the bottom of the [website](https://globalsolaratlas.info/download/world) and download each segment of GeoTIFF file.
2) unzip the files and upload only the global horizontal irradiance tiff files to an image collection folder in Google Earth Engine. Use the following GEE script to mosaic them together

```
//Load in image collection
var ic = ee.ImageCollection('users/resourcewatch/ene_031a_solar_irradiance_GHI);
//Mosaic image
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
  description: 'GHI_250_mosaic',
  assetId: 'users/resourcewatch/ene_031a_solar_irradiance_GHI/GHI_250_mosaic',
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
##### Average daily photovoltaic power potential (30 arcsec resolution)
1) visit the [website](https://globalsolaratlas.info/download/world), under GIS data, download PVOUT-LTAm_AvgDailyTotals(GeoTIFF)
2) unzip the folder
3) upload all 12 tif files to an image collection folder in Google Earth Engine and use this GEE script to mosaic them together
```
//Load in image collection
var ic = ee.ImageCollection('users/resourcewatch/ene_031a_global_solar_atlas_PVOUT);
//Mosaic image
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
  description: 'solar_PVOUT_mosaic',
  assetId: 'users/resourcewatch/ene_031a_global_solar_atlas_PVOUT/solar_PVOUT_mosaic',
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


You can view the processed, Solar Irradiance dataset [here](https://resourcewatch.org/data/explore/Solar-Irradiance).

You can also download original dataset [from the source website](https://globalsolaratlas.info/download/world).

###### Note: This retrieval of and preprocessing of data was documented by [Tina Huang](https://www.wri.org/profile/tina-huang).
