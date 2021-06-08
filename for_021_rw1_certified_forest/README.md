This file describes the data pre-processing that was done to [Certified Forest](https://unstats-undesa.opendata.arcgis.com/datasets/13a621d222c243dc906d7ee53d13eff3) dataset for [display on Resource Watch](https://bit.ly/3xqZ391).

The data was accessed through the source's API and downloaded as a GeoJson file. Below we describe the main steps taken to process the data so that it is formatted correctly to be uploaded to Carto.

1. Read in the data as a geopandas dataframe and subset the dataframe to select only columns of interest. 
2. Convert the table from wide to long form by melting the columns displaying years values into a single year column.
3. Convert the certified area values from thousands of hectares to hectares.
3. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
4. Convert column names to lowercase and replace spaces with underscores to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_021_rw1_certified_forest/for_021_rw1_certified_forest_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3xqZ391).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/for_021_rw1_certified_forest.zip), or [from the source website](https://unstats-undesa.opendata.arcgis.com/datasets/13a621d222c243dc906d7ee53d13eff3).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
