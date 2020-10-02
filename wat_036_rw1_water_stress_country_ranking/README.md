## Water Stress Country Ranking Dataset Pre-processing
This file describes the data pre-processing that was done to [the Aqueduct Country and River Basin Rankings](https://www.wri.org/publication/aqueduct-30) for [display on Resource Watch](https://resourcewatch.org/data/explore/47053e23-7808-40d9-b4ae-1af73c5c8bab).

The source provided the data as an excel file.

Below, we describe the steps used to used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data from the 'results country' sheet of the excel file as a pandas dataframe.
2. Subset the dataframe based on the 'indicator_name' column to select the baseline water stress indicator.
3. Subset the dataframe based on the 'weight' column to select the total gross withdrawal.
4. Replace the '-9999' in the dataframe with nans since they indicate invalid hydrology.
5. Rename the column 'primary' to 'primary_country' since 'primary' is a reserved word in PostgreSQL.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/wat_036_rw1_water_stress_country_ranking/wat_036_rw1_water_stress_country_ranking_processing.py) for more details on this processing.

You can view the processed Water Stress Country Ranking dataset [on Resource Watch](https://resourcewatch.org/data/explore/47053e23-7808-40d9-b4ae-1af73c5c8bab).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/wat_036_rw1_water_stress_country_ranking.zip), or [from the source website](https://www.wri.org/applications/aqueduct/country-rankings/).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid).
