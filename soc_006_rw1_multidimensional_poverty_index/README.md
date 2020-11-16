## Multidimensional Poverty Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Multidimensional Poverty Index](http://hdr.undp.org/en/2020-MPI) for [display on Resource Watch](https://resourcewatch.org/data/explore/d3486db9-5da4-4aee-a363-f71b643a7ce1).

The source provided the data as an excel file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe and remove any notes or empty rows/columns from the data table.
2. Rename column headers to be more descriptive and to remove special characters so that it can be uploaded to Carto without losing information.
3. Split the column 'Year and survey' into two new columns:
  - 'yr_survey', which contains the year
  - 'survey', which contains the survey codes
4. Subset the dataframe to only include data of countries, removing any rows corresponding to regions.
5. Replace the '..', which is used to indicate no-data in the dataframe, with None.
6. Create a new column 'release_dt' to store the year the data was released in as the first date in that year (January 1, XXXX).

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_006_rw1_multidimensional_poverty_index/soc_006_rw1_multidimensional_poverty_index_processing.py) for more details on this processing.

You can view the processed Multidimensional Poverty Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/d3486db9-5da4-4aee-a363-f71b643a7ce1).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_006_rw1_multidimensional_poverty_index.zip), or [from the source website](http://hdr.undp.org/en/2020-MPI).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
