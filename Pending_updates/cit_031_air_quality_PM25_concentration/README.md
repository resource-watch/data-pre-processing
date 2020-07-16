## Air Quality: Surface Fine Particulate Matter (PM2.5) Concentrations Dataset Pre-processing
This file describes the data pre-processing that was done to [the Annual averaged 0.01° × 0.01° w GWR adjustment PM2.5](http://fizz.phys.dal.ca/~atmos/martin/?page_id=140) for [display on Resource Watch](https://resourcewatch.org/data/explore/6e6750da-50c8-4b52-914f-b0d663a7ab59).

Each year of data is provided by the source as a NetCDF file. Before we uploaded each data file to Google Earth Engine, we converted its format from NetCDF to GeoTIFF.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_031_air_quality_PM25_concentration/cit_031_air_quality_PM25_concentration_processing.py) for more details on this processing.

You can view the processed Air Quality: Surface Fine Particulate Matter (PM2.5) Concentrations dataset [on Resource Watch](https://resourcewatch.org/data/explore/6e6750da-50c8-4b52-914f-b0d663a7ab59).

You can also download the original dataset [directly through Resource Watch](http://wri-projects.s3.amazonaws.com/resourcewatch/raster/cit_031_air_quality_PM25_concentration.zip), or [from the source website](http://fizz.phys.dal.ca/~atmos/martin/?page_id=140).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
