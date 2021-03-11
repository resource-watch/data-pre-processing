## Effect of Agricultural Policies on Commodity Prices Dataset Pre-processing
This file describes the data pre-processing that was done to [the Nominal Rate of Protection](http://www.ag-incentives.org/indicator/nominal-rate-protection) for [display on Resource Watch](https://resourcewatch.org/data/explore/641c0a35-f2e5-4198-8ed9-576ea7e9685a).

The data source provided the dataset as one csv file. 

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Import the data as a pandas dataframe.
2. Convert years in the 'year' column to datetime objects and store them in a new column 'datetime'. 
3. Subset the dataframe to retain data that are aggregates of all products at country level.
3. The 'notes' column was removed since it only contains indexes instead of actual data. 
4. The 'productcode' column was removed since it contains the same information as the column 'productname'.
5. The 'source' column was removed since it contains the same information as the column 'sourceversion'
6. The column names were converted to lowercase before we uploaded the data to Carto. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_028_rw1_effect_of_ag_prices_on_commodity_prices/com_028_rw1_effect_of_ag_prices_on_commodity_prices_processing.py) for more details on this processing.

You can view the processed Effect of Agricultural Policies on Commodity Prices dataset [on Resource Watch](https://resourcewatch.org/data/explore/641c0a35-f2e5-4198-8ed9-576ea7e9685a).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/com_028_rw1_effect_of_ag_prices_on_commodity_prices.zip), or [from the source website](http://www.ag-incentives.org/indicator/nominal-rate-protection).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
