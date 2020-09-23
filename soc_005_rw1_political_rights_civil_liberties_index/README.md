## Political Rights and Civil Liberties Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Freedom in the World: The Annual Survey of Political Rights and Civil Liberties](https://freedomhouse.org/report-types/freedom-world) for [display on Resource Watch](https://resourcewatch.org/data/explore/8eafc054-a350-43b5-af61-a64a9a7f8ffe).

The source provided the data as an excel file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.
1. Read in the data as a pandas dataframe and remove all empty columns.
2. Added '_aggr' to the end of the column names 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'CL', 'PR', and 'Total' to match the column names in the previous Carto table.
3. Rename the 'country/territory' and 'c/t?' columns to replace characters unsupported by Carto with underscores.
4. Convert the column names to lowercase letters and replace spaces with underscores.
5. Convert the years in the 'edition' column to datatime objects and store them in a new column 'datetime'.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_005_rw1_political_rights_civil_liberties_index/soc_005_rw1_political_rights_civil_liberties_index_processing.py) for more details on this processing.

You can view the processed Political Rights and Civil Liberties Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/8eafc054-a350-43b5-af61-a64a9a7f8ffe).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/soc_005_rw1_political_rights_civil_liberties_index.zip), or [from the source website](https://freedomhouse.org/report/freedom-world/2020/leaderless-struggle-democracy).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid).
