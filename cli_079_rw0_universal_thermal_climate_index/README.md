## Universal Thermal Climate Index (UTCI) Dataset Pre-processing
This file describes the data pre-processing that was done to [the ERA5-HEAT (Human thErmAl comforT) Universal Thermal Climate Index]({https://cds.climate.copernicus.eu/cdsapp#!/dataset/derived-utci-historical?tab=overview}).

Data was downloaded via the Copernicus Climate Data Store (CDS) API.

Below, we describe the steps used to reformat the raster so that it is formatted correctly for upload to Google Earth Engine.

1. Download netCDF's via CDS API
2. Remove dots in filenames and replace with underscores
3. Convert the Universal Thermal Climate Index (utci variable in netCDF file) from Kelvin to Celsius
4. Calculate daily averages for UTCI
5. Save the daily averages as GeoTIFFs
6. Calculate a monthly average from the daily average GeoTIFFs
7. Save the monthly averages as GeoTIFFs

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cli_079_rw0_universal_thermal_climate_index/cli_079_rw0_universal_thermal_climate_index_processing.py) for more details on this processing.

You can also download the original dataset [from the source website]({https://cds.climate.copernicus.eu/cdsapp#!/dataset/derived-utci-historical?tab=form}).

###### Note: This dataset processing was done by [Alex Sweeney]({https://github.com/alxswny}), and QC'd by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou).
