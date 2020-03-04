## Urban Built-up Area Dataset Pre-processing
This file describes the data pre-processing that was done to the [GHS-BUILT dataset](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) for [display on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

This dataset was provided by the source as a virtual raster (VRT) file along wih separate tiff files that cover the entire region. Since the VRT file was very large, we couldn't convert it directly to a tiff file using GDAL. So, we opted for mosaicing the indvidual tiff files so that we can vizualize the mosaiced version. 

For raster files, we show the data on our platform by pulling from Google Earth Engine (GEE). So, we need to upload these tiff files to Google Earth Engine. And since, we can't directly upload these files to Google Earth Engine from Local, we will upload them to Google Cloud Bucket and then to Google Earth Engine. Please see the [Python script](https://github.com/Taufiq06/data-pre-processing/blob/master/cit_033a_urban_builtup_area/cit_033a_urban_built_up_area_processing.py) for more details on this processing.

One additional note is that we shouldn't try to upload all files to GEE at once. We will run into maximum asset error if we do that. Instead we should distribute the whole task into batches. The steps will be: upload a batch of files, mosaic them, delete individual files that are already mosaiced, continue uploading the next batch of files.

Once each batch of files were uploaded to GEE, a final mosaic was made out of each batches that was eventually displayed on Resource Watch. 

You can view the processed Urban Built-up Area dataset [on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).






