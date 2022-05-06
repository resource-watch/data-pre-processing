## Subnational Human Development Index Dataset Pre-processing
This file describes the data pre-processing that was done to [Subnational Human Development Index](https://globaldatalab.org/shdi/view/shdi/) for [display on Resource Watch](https://bit.ly/3tCh7JU).

The source provided two files, a csv file containing the shdi data and a shapefile containing subnational boundaries used to calculate the index.

The following steps describe the processing performed by the Resource Watch team to the dataset:

1. The shapefile was read as a geopandas dataframe.
2. The csv file was read as a pandas dataframe. Then it was converted from wide to long form by storing the available years into a single column.
3. A column containing the year information as a datetime value was created.
4. The pandas dataframe was formatted to comply with Carto format requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_086_subnational_hdi/soc_086_subnational_hdi_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3tCh7JU).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_086_subnational_hdi.zip), or [from the source website](https://globaldatalab.org/shdi/view/shdi/).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
