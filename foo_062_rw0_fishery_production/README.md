# FISHERY PRODUCTION
This file describes the data pre-processing that was done to [Fishery Production](http://www.fao.org/fishery/statistics/global-production/en) for [display on Resource Watch]().

The source provided this data in three datasets, global (total) fishery production as well as disaggregated data for aquaculture and capture production. The data on global production and capture each provide a CSV providing the quanity of production (tonnes). The data on aquaculture provides two CSVs, on for the quanity of production (tonnes) and the value of production (1000 USD). The data was provided within three zip folders. 

Below we describe the main steps taken to process the data so that it is formatted correctly to be uploaded to Carto.

1. Unzip each  folder and read in the dataset and the country code list as a pandas dataframe.
2. Rename the 'UN_Code' column in the country code list to 'COUNTRY.UN_CODE' so it matches the column header in the dataset.
3. Merge the country code list to the dataset so each row in the dataset is matched with an ISO code and its full name.
4. Add a column to reflect the type of production measured by the value column for the dataset (ex GlobalProduction, Aquaculture, or Capture) and the variable measured (quantity or value).
5. Convert the 'VALUE' column to a float.
6. Concatenate the three dataframes for Global Production, Aquaculture, and Capture. 
7. Rename the 'PERIOD' column to 'year.'
8. Pivot the dataframe from long to short to with country and year as the index, the 'type' of production as the columns, and summed values for each type of production in a given year.
9. Covert all column names to lowercase.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_062_rw0_fishery_production/foo_062_rw0_fishery_production_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch]().

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_062_rw0_fishery_production.zip), or [from the source website](http://www.fao.org/fishery/statistics/global-production/en).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
