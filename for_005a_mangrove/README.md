## Mangrove Forests Data Pre-Processing
This file describes the data pre-processing that was done to [Mangrove Forests dataset](https://data.unep-wcmc.org/datasets/45) for [display on Resource Watch](https://resourcewatch.org/data/explore/386314c4-ab42-47a7-b2cd-596b788e114d).

This dataset was provided by the source as a series of shapefiles, one for each year of data, including 1996, 2007, 2008, 2009, 2010, 2015, and 2016.

In order to upload the selected data on Resource Watch, the following steps were taken:

1. Download and unzip source data.
2. Combine the shapefiles for each year into one shapefile that includes all years of data, and add a column named 'year' to indicate which year each row represents.
3. Overwrite the unique IDs in the table so that there will not be duplicates in the combined file.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_005a_mangrove/for_005a_mangrove_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/386314c4-ab42-47a7-b2cd-596b788e114d).

You can also download original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/for_005a_mangrove.zip), or [from the source website](https://data.unep-wcmc.org/datasets/45).

###### Note: This dataset processing was done by [Kristine Lister](https://www.wri.org/profile/kristine-lister), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
