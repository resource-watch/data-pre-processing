## Urban Built-up Area Dataset Pre-processing
This file describes the data pre-processing that was done to the [GHS-BUILT dataset](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) for [display on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

This dataset was provided by the source as a virtual raster (VRT) file along wih separate tif files that cover the entire region. Since the VRT file was very large, we couldn't convert it directly to a tif file using GDAL. So, we opted for mosaicing the indvidual tiff files so that we can vizualize the mosaiced version. 

For raster files, we usually show the data on resource watch platform by pulling the data from Google Earth Engine (GEE). So, we needed to upload those tiff files to Google Earth Engine. And since, we could't directly upload those files to Google Earth Engine from local directory, we uploaded them to Google Cloud Bucket and then to Google Earth Engine. Please see the [Python script](https://github.com/Taufiq06/data-pre-processing/blob/master/cit_033a_urban_builtup_area/cit_033a_urban_built_up_area_processing.py) for more details on this processing.

One additional note is that we couldn't upload all files to GEE at once. We ran into maximum asset error when I tried to do that. So, instead of uploading them all at once, we distributed the whole task into batches. The steps were: upload a batch of files, mosaic them, delete individual files that are already mosaiced, continue uploading the next batch of files.

Once each batch of files were uploaded to GEE, a final mosaic was made out of each batches that was eventually displayed on Resource Watch. 

You can view the processed Urban Built-up Area dataset [on Resource Watch](https://resourcewatch.org/data/explore/cit033a-Urban-Built-Up-Area_1).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).






