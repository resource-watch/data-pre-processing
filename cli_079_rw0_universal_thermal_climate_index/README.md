## Universal Thermal Climate Index (UTCI) Dataset Pre-processing
This file describes the data pre-processing that was done to [the ERA5-HEAT (Human thErmAl comforT) Universal Thermal Climate Index]({https://cds.climate.copernicus.eu/cdsapp#!/dataset/derived-utci-historical?tab=overview}) for [display on Resource Watch]({link to dataset's metadata page on Resource Watch}).

Data was downloaded via the Copernicus Climate Data Store (CDS) API.

Below, we describe the steps used to {describe how you changed the data, e.g., "combine shapefiles for each continent into one global table on Carto"}.

1. Download netCDF's via CDS API
2. Remove dots in filenames and replace with underscores
3. Convert the Universal Thermal Climate Index (utci variable in netCDF file) from Kelvin to Celsius
4. Calculate daily averages for UTCI
5. Save the daily averages as GeoTIFFs
6. Calculate a monthly average from the daily average GeoTIFFs
7. Save the monthly averages as GeoTIFFs

Please see the [Python script]({link to Python script on Github}) for more details on this processing.

You can view the processed {Resource Watch public title} dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website]({https://cds.climate.copernicus.eu/cdsapp#!/dataset/derived-utci-historical?tab=form}).

###### Note: This dataset processing was done by [Alex Sweeney]({https://github.com/alxswny}), and QC'd by [{name}]({link to WRI bio page}).
