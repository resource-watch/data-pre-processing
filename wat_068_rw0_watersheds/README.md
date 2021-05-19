## Watersheds Data Pre-Processing
This file describes the data pre-processing for the [HydroBASINS](https://www.hydrosheds.org/page/hydrobasins) dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/ab6216ee-9a2b-412f-b538-8644d5834c7a).

The source provided data as regional tiles in individual polygon shapefiles, one for each
region and each Pfafstetter level. 

Due to the size of the sub-basins, the breakdowns provided by levels 3-8 are most relevant for analysis, and were thus selected for display on Resource Watch. 

Below, we describe the steps used to reformat the shapefiles to upload them to Carto.

1. For each relevant basin level, read in the shapefiles for the nine regional tiles as a geopandas dataframe.
2. Combine shapefiles for each basin level into one shapefile that includes all regional tiles, with a column for 'level' to indicate which level the file represents.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/wat_068_rw0_watersheds/wat_068_rw0_watersheds_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/ab6216ee-9a2b-412f-b538-8644d5834c7a).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/wat_068_rw0_watersheds.zip), or [from the source website](https://www.dropbox.com/sh/hmpwobbz9qixxpe/AACPCyoHHAQUt_HNdIbWOFF4a/HydroBASINS/standard?dl=0&subfolder_nav_tracking=1).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
