## Population (Grid, 100m) Dataset Pre-processing
This file describes the data pre-processing that was done to [Population Count - Constrained Individual Countries](https://www.worldpop.org/geodata/listing?id=78) for [display on Resource Watch](https://resourcewatch.org/data/explore/d6e42176-90c4-429d-8cae-7619c545a458).

The source provided the data as a [Google Earth Engine image collection](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop). The images in the image collection were mosaiced together for display on Resource Watch using the following code.

```javascript
// Purpose: Mosaic an image collection of tif files and export them to an asset


// Mosaic an image collection

//Load in a batch of image collection
var ic = ee.ImageCollection('WorldPop/GP/100m/pop');

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
  description: 'Population_grid_100m',
  assetId: 'projects/resource-watch-gee/soc_107_population',
  crs: crs,
  crsTransform: transform,
  region: bounds,
  maxPixels: 1e13
});

```

You can view the processed Population (Grid, 100m) dataset [on Resource Watch](https://resourcewatch.org/data/explore/d6e42176-90c4-429d-8cae-7619c545a458).

You can also download the original dataset [from the source website](https://www.worldpop.org/geodata/listing?id=78).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
