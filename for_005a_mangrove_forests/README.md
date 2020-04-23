## Mangrove Forests Data Pre-Processing
This file describes the data pre-processing that was done to [Mangrove Forests dataset](https://data.unep-wcmc.org/datasets/45) for [display on Resource Watch](https://resourcewatch.org/data/explore/386314c4-ab42-47a7-b2cd-596b788e114d).

This dataset was provided by the source as a series of shapefiles, one for each year of data, including 1996, 2007, 2008, 2009, 2010, 2015, and 2016. Data from these shapefiles was uploaded to the Resource Watch Carto account to connect to our API. In the process the unique IDs of each shapefile were overwritten in order for the merged dataset on Carto to have unique IDs.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_005a_mangrove_forests/for_005a_mangrove_forests.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/386314c4-ab42-47a7-b2cd-596b788e114d).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/for_005a_mangrove_forests.zip), or [from the source website](https://data.unep-wcmc.org/datasets/45).

###### Note: This dataset processing was done by [Kristine Lister](https://www.wri.org/profile/kristine-lister), and QC'd by [insert name of QC person](https://www.wri.org/profile/firstname-lastname).
