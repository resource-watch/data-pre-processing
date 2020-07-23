## Sea Surface Temperature Variability Dataset Pre-processing
This file describes the data pre-processing that was done to the [Thermal History - SST Variability (1985-2018)](https://coralreefwatch.noaa.gov/product/thermal_history/sst_variability.php) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is contained within a NetCDF file. The following variables are shown on Resource Watch:
- Sea Surface Temperature - Warmest Month Variability (stdv_maxmonth): Fluctuation in average SST during the warmest month of each year, from year to year (1985-2018), in areas containing coral reefs
- Sea Surface Temperature - Annual Variability (stdv_annual): Fluctuation in average SST across the entire year, from year to year (1985-2018), in areas containing coral reefs

To process this data for display on Resource Watch, the NetCDF file was downloaded. The relevant subdatasets were extracted to individual, single-band GeoTIFFs, as was a "mask" showing the extent of the dataset (which covers only areas containing coral reefs). These GeoTIFF files were masked accordingly, then merged into a single multi-band GeoTIFF, with separate bands containing the data for each variable.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_009_sea_surface_temperature_variability/ocn_009_sea_surface_temperature_variability_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original data [from the source website](https://coralreefwatch.noaa.gov/product/thermal_history/sst_variability.php).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid) and [Peter Kerins](https://www.wri.org/profile/peter-kerins).