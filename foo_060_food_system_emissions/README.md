This file describes the data pre-processing that was done to [Food System Emissions](https://edgar.jrc.ec.europa.eu/edgar_food#wtsau) for [display on Resource Watch](https://bit.ly/3fXLxlg).

The source provided this dataset as an excel file, containing data from 1990-2015. Below, we describe the main actions performed to process the data before uploading it to Carto.

1. Convert the dataframe from wide form to long form, in which one column indicates the year.
2. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
3. Convert the column headers to lowercase to match Carto column name requirements.
4. Replace NaN in the table with None.
Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/master/foo_060_food_system_emissions_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3fXLxlg).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_060_food_system_emissions.zip), or [from the source website](https://edgar.jrc.ec.europa.eu/edgar_food#wtsau).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
