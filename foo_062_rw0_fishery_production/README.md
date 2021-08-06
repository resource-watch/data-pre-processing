# FISHERY PRODUCTION
This file describes the data pre-processing that was done to [Fishery Production](http://www.fao.org/fishery/statistics/global-production/en) for [display on Resource Watch](https://resourcewatch.org/data/explore/ac9c2f07-9f23-4a33-9958-e02c571ec009).

The source provided the data as four CSV files within zipped folders.  One CSV contains the data for global (total) production as the quantity of production (tonnes). One contains the data for capture production as the quantity of production (tonnes). And the other two CSVs contain data for aquaculture as the quantity of production (tonnes) and the value of production (1000 USD). 

Below we describe the main steps taken to process the data so that it is formatted correctly to be uploaded to Carto.

1. Unzip each folder and read in the dataset and the country code list as a pandas dataframe.
2. Rename the 'UN_Code' column in the country code list to 'COUNTRY.UN_CODE' so it matches the column header in the dataset.
3. Merge the country code list to the dataset so each row in the dataset is matched with an ISO code and its full name.
4. Add a column to reflect the type of production measured by the value column for the dataset (ex GlobalProduction, Aquaculture, or Capture) and the variable measured (quantity or value).
5. Convert the data type of the 'VALUE' column to float.
6. Concatenate the three dataframes for Global Production, Aquaculture, and Capture. 
7. Rename the 'PERIOD' column to 'year'.
8. Pivot the dataframe from long to wide form to sum the values for each type of production in a given year for each country.
9. Convert all column names to lowercase to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_062_rw0_fishery_production/foo_062_rw0_fishery_production_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/ac9c2f07-9f23-4a33-9958-e02c571ec009).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_062_rw0_fishery_production.zip), or [from the source website](http://www.fao.org/fishery/statistics/global-production/en).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [ Yujing Wu](https://www.wri.org/profile/yujing-wu).
