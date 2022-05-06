## Refugees and Internally Displaced Persons Dataset Pre-processing
This file describes the data pre-processing that was done to [IDMC data on Internally Displaced Persons and the demographic data for the population and solutions datasets](https://www.unhcr.org/refugee-statistics/download) for display on Resource Watch as the following datasets:

- [Host Countries of Refugees and Internally Displaced Persons](https://resourcewatch.org/data/explore/c856396d-d0f2-4aae-9671-4903b2ebed4d).
- [Origin Countries of Refugees and Internally Displaced Persons](https://resourcewatch.org/data/explore/7a8b5296-d283-4832-9be1-edd760bbb58f)

The original data is downloadable in a .csv format.  

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to carto:
1. Merge "population.csv" and "solution.csv" files as a single pandas dataframe based on the columns: "year", "country of origin" and "country of asylum".
2. Sum into "refugees_incl_refugee_like_situations" the following columns: 'refugees under unhcr_s mandate','venezuelans displaced abroad','resettlement arrivals'.
3. Create a column "total_population" encompassing the sum of the other columns.
4. Trim unwanted characters and spaces to comply with Carto's column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_043_rw0_refugees_internally_displaced_persons/soc_043_rw0_refugees_internally_displaced_persons_processing.py) for more details on this processing.

You can view the processed datasets on Resource Watch:
- [Host Countries of Refugees and Internally Displaced Persons](https://resourcewatch.org/data/explore/c856396d-d0f2-4aae-9671-4903b2ebed4d).
- [Origin Countries of Refugees and Internally Displaced Persons](https://resourcewatch.org/data/explore/7a8b5296-d283-4832-9be1-edd760bbb58f)

You can also download original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_043_rw0_refugees_internally_displaced_persons.zip), or [from the source website](https://www.unhcr.org/refugee-statistics/download).

###### ###### Note: This dataset processing and qc was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes).
