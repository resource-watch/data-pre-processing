## Human Development Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Human Development Index (HDI)](http://hdr.undp.org/en/2019-report) for [display on Resource Watch](https://resourcewatch.org/data/explore/fc6dea95-37a6-41a0-8c99-38b7a2ea7301).

The source provided the data in a csv format.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe.
2. Remove empty columns from the dataframe.
3. Remove empty rows and rows that only contain metadata.
4. Replace the '..', which is used to indicate no-data, in the dataframe with None.
5. Convert the data type of the column 'HDI Rank' to integer.
6. Convert the dataframe from wide to long format so there will be one column indicating the year and another column indicating the index.
7. Rename the 'variable' and 'value' columns created in the previous step to 'year' and 'yr_data'.
8. Convert the data type of the 'year' column to integer.
9. Convert the years in the 'year' column to datetime objects and store them in a new column 'datetime'.
10. Convert the data type of column 'yr_data' to float.
11. Rename the column 'HDI Rank' to 'hdi_rank' since space within column names is not supported by Carto.
12. Rename the column 'Country' to 'country_region' since the column contains both countries and regions.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_004_rw1_human_development_index/soc_004_rw1_human_development_index_processing.py) for more details on this processing.

You can view the processed Human Development Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/fc6dea95-37a6-41a0-8c99-38b7a2ea7301).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_004_rw1_human_development_index.zip), or [from the source website](http://hdr.undp.org/en/indicators/137506#).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
