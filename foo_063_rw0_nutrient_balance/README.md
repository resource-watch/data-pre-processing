## Nutrient Balance Dataset Pre-processing
This file describes the data pre-processing that was done to [the Nutrient Balance Agriculture-Environmental Indicator](https://data.oecd.org/agrland/nutrient-balance.htm) for [display on Resource Watch]({}).

The data was provided by the source as a CSV.

Below, we describe the steps used to process the data for upload to Carto.

1. Read in the data as a pandas data frame.
2. Subset the data to high level indicators ('I0' - 'Nutrient inputs', 'OO' - 'Nutrient outputs, 'B0' - 'Balance (inputs minus outputs)' 'BPERHA' - 'Balance per hectare')
3. Rename the column 'COUNTRY' to 'iso'.
4. Remove duplicate and blank columns.
5. Comvert all column names to lowercase to match Carto column name requirements.
6. Convert 'time' column to date time object.

Please see the [Python script]() for more details on this processing.

You can view the processed Nutrient Balance dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/foo_063_rw0_nutrient_balance.zip), or [from the source website](https://stats.oecd.org/viewhtml.aspx?datasetcode=AEI_NUTRIENTS&lang=en).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [{name}]({link to WRI bio page}).
