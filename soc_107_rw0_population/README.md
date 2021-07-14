## Population (Grid, 100m) Dataset Pre-processing
This file describes the data pre-processing that was done to [Population Count - Constrained Individual Countries](https://www.worldpop.org/geodata/listing?id=78) for [display on Resource Watch](https://resourcewatch.org/data/explore/d6e42176-90c4-429d-8cae-7619c545a458).

The source provided the data as a [Google Earth Engine image collection](https://developers.google.com/earth-engine/datasets/catalog/WorldPop_GP_100m_pop). The images in the image collection were mosaiced together for display on Resource Watch using the following code.

```javascript
// Purpose: Mosaic all images for all years within an image collection and export it to an asset
with each year of data as a band
//Load in an image collection
var worldpop = ee.ImageCollection('WorldPop/GP/100m/pop');

// Save the dates of the time series
var yearStart = 2000;
var yearEnd = 2020;

// Filter images for the year 2000 and mosaic all the images for the year to a single image. This image will serve as the base band for the compiled set of images. 
var yearStack = worldpop.filterMetadata('year','equals',yearStart)
                .mosaic()
                .rename('Y'+ [yearStart.toString()]);

// For each year in the time series, filter the data to that year, mosaic all the images to a single image, and add the mosaicked image as a band to the compiled image.
for (var i = yearStart; i <= yearEnd; i++) {
    var yearCollection = worldpop.filterMetadata('year', 'equals', i);
    var yearImage = yearCollection.mosaic().rename('Y'+ [i.toString()]);
    yearStack = yearStack.addBands(yearImage, null, true);
}

//Save the boundaries.
var rect = [-180, -60, 180, 89.9];
var bounds = ee.Geometry.Rectangle(rect,null,false);

//Export mosaicked image to an asset with boundaries obtained in the previous step.
Export.image.toAsset({
  image: yearStack,
  description: 'Population_grid_100m',
  assetId: 'projects/resource-watch-gee/soc_107_population',
  region: bounds,
  maxPixels: 1e13
});

```

You can view the processed Population (Grid, 100m) dataset [on Resource Watch](https://resourcewatch.org/data/explore/d6e42176-90c4-429d-8cae-7619c545a458).

You can also download the original dataset [from the source website](https://www.worldpop.org/geodata/listing?id=78).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
