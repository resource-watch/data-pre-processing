## Maritime Boundaries Dataset Pre-processing
This file describes the data pre-processing that was done to [the Maritime Boundaries version 11](https://www.marineregions.org/sources.php#marbound) for [display on Resource Watch](https://resourcewatch.org/data/explore/6af67024-b917-4944-851a-152b566ff1a8).

The data source provided the dataset as three shapefiles. 

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Import the polygon shapefiles as geopandas dataframes.
2. Stack the three geopandas dataframes on top of each other.
3. Project the data so its coordinate system is WGS84.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.
5. Reorder columns by their column names.
6. Convert the column names to lowercase to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_011_rw1_maritime_boundaries/com_011_rw1_maritime_boundaries_processing.py) for more details on this processing.

You can view the processed Maritime Boundaries dataset [on Resource Watch](https://resourcewatch.org/data/explore/6af67024-b917-4944-851a-152b566ff1a8).

You can also download the original dataset [from the source website](https://www.marineregions.org/downloads.php).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
