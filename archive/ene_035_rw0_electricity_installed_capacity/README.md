## Electricity Installed Capacity Dataset Pre-processing
This file describes the data pre-processing that was done to [the Electricity Installed Capacity](https://www.eia.gov/international/data/world/electricity/electricity-capacity) for [display on Resource Watch](http://resourcewatch.org/data/explore/683aa637-aa4f-46ab-8260-4441de896131).

The data was provided by the source through its API in a json format.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto. We read in the data as a pandas dataframe, deleted rows without data, and removed data of regions that consist of multiple geographies. A new column 'datetime' was created to store the time period of the data as the first date of the year. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ene_035_rw0_electricity_installed_capacity/ene_035_rw0_electricity_installed_capacity_processing.py) for more details on this processing.

You can view the processed Electricity Installed Capacity dataset [on Resource Watch](http://resourcewatch.org/data/explore/683aa637-aa4f-46ab-8260-4441de896131).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/ene_035_rw0_electricity_installed_capacity.zip), or [from the source website](https://www.eia.gov/international/data/world/electricity/electricity-capacity).

This script has been archived since we are managing all the EIA datasets on Resource Watch together using [upload_eia_data](https://github.com/resource-watch/nrt-scripts/tree/master/upload_eia_data).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
