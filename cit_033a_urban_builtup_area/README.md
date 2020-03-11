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
`
`
3) Delete all the images that were used in the mosaic.
4) Repeat steps 1-3 until all tiles had been uploaded and mosaicked in GEE.

Once all of the tiles were uploaded to GEE, a final mosaic with global coverage was made out of each of batches. This final mosaic is what is displayed on Resource Watch. 

You can view the processed Urban Built-up Area dataset [on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
