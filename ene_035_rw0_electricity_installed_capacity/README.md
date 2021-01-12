## Electricity Installed Capacity Dataset Pre-processing
This file describes the data pre-processing that was done to [the Electricity Installed Capacity](https://www.eia.gov/international/data/world/electricity/electricity-capacity) for [display on Resource Watch](http://resourcewatch.org/data/explore/683aa637-aa4f-46ab-8260-4441de896131).

The data was provided by the source through its API in a json format.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto. We read in the data as a pandas dataframe, deleted rows without data, and removed data of regions that consist of multiple geographies.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ene_035_rw0_electricity_installed_capacity/ene_035_rw0_electricity_installed_capacity_processing.py) for more details on this processing.

You can view the processed {Resource Watch public title} dataset [on Resource Watch](http://resourcewatch.org/data/explore/683aa637-aa4f-46ab-8260-4441de896131).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/ene_035_rw0_electricity_installed_capacity.zip), or [from the source website](https://www.eia.gov/international/data/world/electricity/electricity-capacity).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
