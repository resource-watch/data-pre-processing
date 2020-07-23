## Historical Coral Bleaching Stress Frequency Dataset Pre-processing
This file describes the data pre-processing that was done to the [Thermal History - Stress Frequency (1985-2018), Version 2.1](https://coralreefwatch.noaa.gov/product/thermal_history/stress_frequency.php) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is provided by the source as a netcdf file. The following variables are shown on Resource Watch:
- n_gt0: The number of events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
- n_ge4: The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
- n_ge8: The number of events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
- rp_gt0: The average time between events for which the thermal stress, measured by Degree Heating Weeks, exceeded 0 degC-weeks.
- rp_ge4: The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 4 degC-weeks.
- rp_ge8: The average time between events for which the thermal stress, measured by Degree Heating Weeks, reached or exceeded 8 degC-weeks.
        
To process this data for display on Resource Watch, the data in each of these netcdf variables is first converted to individual tif files. Then, these individual tif files are merged into a single tif file with a band for each variable.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_008_historic_coral_bleaching_stress_frequency/ocn_008_historic_coral_bleaching_stress_frequency_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/4c64fb3d-a05e-45ef-b886-2a75f418e00b).

You can also download original dataset [from the source website](ftp://ftp.star.nesdis.noaa.gov/pub/sod/mecb/crw/data/thermal_history/v2.1).

###### Note: This dataset processing was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
