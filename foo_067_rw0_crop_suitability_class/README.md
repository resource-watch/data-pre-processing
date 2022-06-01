## Crop Suitability Class Dataset Pre-processing
This file describes the data pre-processing that was done to the [Crop Suitability Class](https://gaez-data-portal-hqfao.hub.arcgis.com/pages/theme-details-theme-4).

The source provided the data in multiple TIFF files available for download via URL. The TIFFs show crop suitability index for multiple timeframes and input technologies. Only files encompassing cotton, coffee, and rice were downloaded.

Below, we describe the steps used to reformat the table so that it is formatted correctly for upload to Google Earth Engine.

1. Run the rice_ensemble_processing.py script first.
   1. This script downloads wetland and dryland rice GeoTIFFS that were produced from various climate models from the source.
   2. It computes the average of the input GeoTIFFS. This is done for each timeframe, RCP scenario, watering regime, and crop.
   3. Saves the average of the models to a new GeoTIFF that has "ensemble" in the beginning of its name.
2. Run the foo_067_rw0_global_crop_suitability_class_processing.py script.
   1. This script downloads historic GeoTiffs for all crops, and ensemble GeoTIFFS for cotton and coffee from the source.
   2. Adds in the ensemble GeoTIFFs that were created from rice_ensemble_processing.py for bulk upload.
   3. Upload files to GEE.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_067_rw0_global_crop_suitability_class/foo_067_rw0_global_crop_suitability_class_processing.py) for more details on this processing.

You can also download the original dataset [from the source website](https://gaez-data-portal-hqfao.hub.arcgis.com/pages/data-viewer).

###### Note: This dataset processing was done by [Alex Sweeney](https://github.com/alxswny) and [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Chris Rowe](https://www.wri.org/profile/chris-rowe).
