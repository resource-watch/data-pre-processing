# Food Insecurity Processing 
This file describes the data pre-processing that was done to the [Suite of Food Security Indicators](http://www.fao.org/faostat/en/#data/FS) for display [on Resource Watch](https://resourcewatch.org/data/explore/).

The source provided the data as a CSV file within a zipped folder.

Below we describe the main steps taken to process the data and for upload to Carto.

1. Read in the data as a pandas dataframe.
2. Subset the dataframes to only include the indicator 'Prevalence of severe food insecurity in the total population, 3-year averages'.
3. Subset the dataframes to only include country and global level information, not regions or continents.
4. Convert column names to lowercase and replace spaces with underscores to match Carto column name requirements.
5. Select the columns with values for the indicator, which is caluclated for 3-year averages (2014-2016, 2015-2017, 2016-2018, 20172019, 2018-2020)


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_064_rw0_food_insecurity/foo_061_rw0_marine_food_supply_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_064_rw0_food_insecurity.zip), or [from the source website](http://www.fao.org/faostat/en/#data/FS).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [ ]().
