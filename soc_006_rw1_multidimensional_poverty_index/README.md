## Multidimensional Poverty Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Multidimensional Poverty Index](http://hdr.undp.org/en/2020-MPI) for [display on Resource Watch](https://resourcewatch.org/data/explore/d3486db9-5da4-4aee-a363-f71b643a7ce1).

The source provided the data as an excel file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe.
2. Remove empty columns and rows that contain only notes instead of actual data.
4. Combine the strings in the first 4 rows of the dataframe to create headers.
5. Remove the first 4 rows of the dataframe.
6. Remove columns that contain footnotes instead of actual data.
7. Extract the year values from the column 'Year and survey'(now 'Multidimensional Poverty IndexYear and survey2008-2019') and store them in a new column 'yr_survey'.
8. Extract the survey codes from the column 'Year and survey'(now 'Multidimensional Poverty IndexYear and survey2008-2019') and store them in a new column 'survey'.
9. Drop the columns 'index' and 'Year and survey'(now 'Multidimensional Poverty IndexYear and survey2008-2019').
10. Rename the columns to be more concise.
11. Replace '%' in column names with '_percent' and replace spaces and special characters with underscores.
12. Subset the dataframe to only include data of countries.
13. Replace the '..', which is used to indicate no-data, in the dataframe with None.
14. Except the columns 'country', 'survey', and 'yr_survey', set the data type of the columns to float.
15. Create a new column 'release_dt' to store the year the data was released in as the first date in that year.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_006_rw1_multidimensional_poverty_index/soc_006_rw1_multidimensional_poverty_index_processing.py) for more details on this processing.

You can view the processed Multidimensional Poverty Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/d3486db9-5da4-4aee-a363-f71b643a7ce1).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_006_rw1_multidimensional_poverty_index.zip), or [from the source website](http://hdr.undp.org/en/2020-MPI).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
