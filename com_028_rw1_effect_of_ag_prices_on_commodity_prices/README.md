## Effect of Agricultural Policies on Commodity Prices Dataset Pre-processing
This file describes the data pre-processing that was done to [the Nominal Rate of Protection](http://www.ag-incentives.org/indicator/nominal-rate-protection) for [display on Resource Watch]({link to dataset's metadata page on Resource Watch}).

The data source provided the dataset as one csv file and one README file. The csv file was reformated to upload to Carto. We converted the years in the 'year' column to datetime objects and store them in a new column 'datetime'. The column names were converted to lowercase before we uploaded it to Carto. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_028_rw1_effect_of_ag_prices_on_commodity_prices/com_028_rw1_effect_of_ag_prices_on_commodity_prices_processing.py) for more details on this processing.

You can view the processed Effect of Agricultural Policies on Commodity Prices dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/com_028_rw1_effect_of_ag_prices_on_commodity_prices.zip), or [from the source website](http://www.ag-incentives.org/indicator/nominal-rate-protection).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [{name}]({link to WRI bio page}).
