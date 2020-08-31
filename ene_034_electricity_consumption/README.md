## Electricity Consumption Dataset Pre-processing
This file describes the data pre-processing that was done to the [U.S. Energy Information Administration (EIA) International Energy Statistics Electricity Net Consumption dataset](https://www.eia.gov/beta/international/data/browser/#/?pa=0000002&c=ruvvvvvfvtvnvv1vrvvvvfvvvvvvfvvvou20evvvvvvvvvvvvuvs&ct=0&tl_id=2-A&vs=INTL.2-2-AFG-BKWH.A&vo=0&v=H&start=1980&end=2016) for [display on Resource Watch](https://resourcewatch.org/data/explore/eef10736-8d8b-4ac9-a715-ef0653a83196).

This dataset was provided by the source as a csv, which you can download using the link above. The csv table was converted from wide to long form, using Python. A new column 'electricity_consumption_ktoe' has also been created in Python to show the electricity consumption in Kilotonne of Oil Equivalent (ktoe).

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ene_034_electricity_consumption/ene_034_electricity_consumption_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/eef10736-8d8b-4ac9-a715-ef0653a83196).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/ene_034_electricity_consumption.zip), or [from the source website](https://www.eia.gov/international/data/world/electricity/electricity-consumption?pd=2&p=0000002&u=0&f=A&v=mapbubble&a=-&i=none&vo=value&&t=C&g=00000000000000000000000000000000000000000000000001&l=249-ruvvvvvfvtvnvv1vrvvvvfvvvvvvfvvvou20evvvvvvvvvvvvvvs&s=315532800000&e=1514764800000
).

###### Note: This dataset processing was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
