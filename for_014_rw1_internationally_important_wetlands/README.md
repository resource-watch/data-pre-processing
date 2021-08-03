## Ramsar Internationally Important Wetlands Dataset Pre-processing
This file describes the data pre-processing that was done to [the Wetlands of International Importance (the Ramsar List)](http://www.ramsar.org/about/wetlands-of-international-importance-ramsar-sites) for [display on Resource Watch](https://resourcewatch.org/data/explore/2ac1f43c-30bc-4ed9-846c-8443ce4987a9).

The data source provided the dataset as one csv file. 

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Import the data as a pandas dataframe.
2. Create a new column 'wetland_type_general' of general wetland type for visualization.
3. Replace the 'nan' in column 'wetland_type_general' with 'Other'.
4. Replace NaN in the table with None.
5. Replace whitespaces in column names with underscores and convert the column names to lowercase to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_014_rw1_internationally_important_wetlands/for_014_rw1_internationally_important_wetlands_processing.py) for more details on this processing.

You can view the processed Ramsar Internationally Important Wetlands dataset [on Resource Watch](https://resourcewatch.org/data/explore/2ac1f43c-30bc-4ed9-846c-8443ce4987a9).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/for_014_rw1_internationally_important_wetlands.zip), or [from the source website](https://rsis.ramsar.org/?pagetab=3).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
