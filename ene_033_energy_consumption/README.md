## Energy Consumption Dataset Pre-processing
This file describes the data pre-processing that was done to the [U.S. Energy Information Administration (EIA) International Energy Statistics Total Energy Consumption dataset](https://www.eia.gov/beta/international/data/browser/#/?pa=000000001&c=ruvvvvvfvtvnvv1urvvvvfvvvvvvfvvvou20evvvvvvvvvnvvuvs&ct=0&ug=4&vs=INTL.44-2-AFG-QBTU.A&cy=2017&vo=0&v=H&start=1980&end=2017) for [display on Resource Watch](https://resourcewatch.org/data/explore/67cf410f-4cdf-4437-aa09-187e5fa590ae).

This dataset was provided by the source as a csv, which you can download using the link above. The csv table was converted from wide to long form, using Python.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ene_033_energy_consumption/ene_033_energy_consumption_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/67cf410f-4cdf-4437-aa09-187e5fa590ae).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/ene_033_energy_consumption.zip), or [from the source website](https://www.eia.gov/beta/international/data/browser/#/?pa=000000001&c=ruvvvvvfvtvnvv1urvvvvfvvvvvvfvvvou20evvvvvvvvvnvvuvs&ct=0&ug=4&vs=INTL.44-2-AFG-QBTU.A&cy=2017&vo=0&v=H&start=1980&end=2017).

###### Note: This dataset processing was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).