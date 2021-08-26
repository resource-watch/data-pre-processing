# Shipping Emissions
This file describes the pre-processing performed on [Shipping Emissions data](https://stats.oecd.org/index.aspx?queryid=73644) for ingestion into [Resource Watch](https://resourcewatch.org/data/explore/c9937085-22ec-4f8c-b819-5fa02473abdb).

The source provided the data as a single CSV file, which contained country-/territory-level time series data for a variety of indicators related to transportation and emissions. We extracted a single indicator, `IND-ENE-MAR`, which describes the "share of CO2 emissions from international maritime bunkers in total CO2 emissions". The time series data for all countries was saved in a standalone CSV file, which was then uploaded to Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_038_rw0_shipping_emissions/com_038_rw0_shipping_emissions.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/ac9c2f07-9f23-4a33-9958-e02c571ec009).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_062_rw0_fishery_production.zip), or [from the source website](http://www.fao.org/fishery/statistics/global-production/en).

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).
