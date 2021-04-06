## Active Fault Lines Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Earthquake Model Global Active Fault](https://github.com/GEMScienceTools/gem-global-active-faults/tree/2019.0) for [display on Resource Watch](https://resourcewatch.org/data/explore/c86b1409-7ddb-4ec2-b2fd-bf035db325b6).

The data source provided the dataset as one shapefile. 

Below, we describe the steps used to reformat the shapefile so that it is formatted correctly to upload to Carto.

1. Import the line shapefile as a geopandas dataframe.
2. Project the data so its coordinate system is WGS84.
3. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.
4. Reorder columns by their column names.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/dis_016_rw1_active_fault_lines/dis_016_rw1_active_fault_lines_processing.py) for more details on this processing.

You can view the processed Active Fault Lines dataset [on Resource Watch](https://resourcewatch.org/data/explore/c86b1409-7ddb-4ec2-b2fd-bf035db325b6).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/dis_016_rw1_active_fault_lines.zip), or [from the source website](https://zenodo.org/record/3376300).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
