## Standard Precipitation Index Data Retrieval and Data Pre-processing
This file describes the process used to retrieve and preprocess Standard Precipitation Index from the [the CHIRPS precipitation dataset](https://pubs.usgs.gov/ds/832/) for [display on Resource Watch](https://resourcewatch.org/data/explore/cli023-Standard-Precipitation-Index).

The Standard Precipitation Index dataset is calculated from CHIRPS precipitation data, using the [Climate Engine app](https://app.climateengine.org/climateEngine). Below, we list the parameters used in the Climate Engine app to produce and download the data shown on Resource Watch.

##### Variable
```
Type: Climate
Dataset: CHIRPS - Pentad
Variable: Standard Precipiation Index (SPI)
Computation Resolution (Scale): 4800 m (1/20-deg)
```
##### Processing
```
Statistic (over day range): No Statistic
Calculation: Standardized Index
```
##### Time Period
```
Season: Custom Date Range
Start Date: {YEAR}-01-01
End Date: {YEAR}-12-31
Year Range for Historical Avg/Distribution: 1981-2006
```
In the Time Period variables, above, the {YEAR} for Start Date and End Date should be replaced with the year for which you are currently pulling data.

The 'Get Map Layer' button was then used to produce a map of the Standard Precipitation Index data.

At the top of the page, the 'Download' tab was used to download the data for the following rectangular regions. It is impossible to download the image for the whole world, because the output of image computation will be too large and corrupted files will be generated. As a result, the following eight rectangular regions were used to download eight separate images.
```
SPI_2019_1:
NE corner: 50N, -90E
SW corner: 0N, -180E

SPI_2019_2:
NE corner: 50N, 0E
SW corner: 0N, -90E

SPI_2019_3:
NE corner: 50N, 90E
SW corner: 50N, 180E

SPI_2019_4:
NE corner: 0N, -180E
SW corner: 0N, 90E

SPI_2019_5:
NE corner: 0N, -90E
SW corner: -50N, -180E

SPI_2019_6:
NE corner: 0N, 0E
SW corner: -50N, -90E

SPI_2019_7:
NE corner: 0N, 90E
SW corner: -50N, 0E

SPI_2019_8:
NE corner: 0N, 180E
SW corner: -50N, 90E

```
Upload eight images to Google Earth Engine under the same Image Collection folder and mosaic them together using the following code:
```
//Load in image collection
var ic = ee.ImageCollection('users/resourcewatch/cli_023_SPI_2019_mosaic');
//Mosaic image
var mosaic = ic.mosaic();
print(mosaic)

//Get projection
var projection = ic.first().projection();
var crs = projection.getInfo().crs;
var transform = projection.getInfo().transform;
//Save global bounds
var rect = [-180, -50, 180, 50];
var bounds = ee.Geometry.Rectangle(rect,null,false);
//Export image
Export.image.toAsset({
  image: mosaic,
  description: 'cli_023_CHIRPS_2019_annual_SPI',
  assetId: 'users/resourcewatch/cli_023_CHIRPS_2019_annual_SPI',
  crs: crs,
  crsTransform: transform,
  region: bounds,
  maxPixels: 1e13
});
```

You can view the processed, Standard Precipitation Index dataset [here](https://resourcewatch.org/data/explore/cli023-Standard-Precipitation-Index).

You can also download original dataset [from the source website](https://app.climateengine.org/climateEngine).

###### Note: This retrieval of this data was originally done by [Nathan Suberi](https://www.wri.org/profile/nathan-suberi). The retrieval process was documented by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder). This retrieval and pre-processing process is updated by [Tina Huang](https://www.wri.org/profile/tina-huang).
