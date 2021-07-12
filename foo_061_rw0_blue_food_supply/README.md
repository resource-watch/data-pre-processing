# Food from the Sea (Blue Food Supply)
This file describes the data pre-processing that was done to the [New](http://www.fao.org/faostat/en/#data/FBS) and [Historic](http://www.fao.org/faostat/en/#data/FBSH) Food Balance Sheets for displaying the Food from the Sea dataset [on Resource Watch](https://resourcewatch.org/data/explore/24ad32a0-b25f-44ff-9bc0-2650ea29e0b4).

The source provided two datasets, one for years collected with historic methodology and one for years collected with new methodology, as two CSV files within two zipped folders.

Below we describe the main steps taken to process the data and combine the two files to upload the data to Carto.

1. Read in the data as pandas dataframes and subset the dataframes to only include values for food supply and protein supply. 
2. Subset the dataframes to only include ocean-sourced food products and grand totals.
3. Subset the dataframes to only include country and global level information, not regions or continents.
4. Create a column called "Type" to distinguish between ocean-sourced total and grand total values.
5. Join the dataframes for the historic and new data, and sort by country, year, and type.
6. Rename the 'Year code' column to 'Year'.
7. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
8. Convert the value column to float.
9. Convert column names to lowercase and replace spaces with underscores to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_061_rw0_marine_food_supply/foo_061_rw0_marine_food_supply_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/24ad32a0-b25f-44ff-9bc0-2650ea29e0b4).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_061_rw0_marine_food_supply.zip), or [from the source website](http://www.fao.org/faostat/en/#data/FBS).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/Yuging-Wu).
