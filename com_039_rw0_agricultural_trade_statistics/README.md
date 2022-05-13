## Agriculture Trade Statistics Dataset Pre-processing
This file describes the data pre-processing that was done to [the Agricultural Trade Statistics]({learn more link}) for [display on Resource Watch]({link to dataset's metadata page on Resource Watch}).

The data source provided the dataset as one CSV file.

Below, we describe the steps used to reformat the table so that it is formatted correctly for upload to Carto.

1. Import the data as a pandas dataframe.
2. Convert column headers to lower case.
3. Rename 'area' column to 'country'.
4. Remove whitespaces, parentheses, and add underscores from column headers.
5. Convert years in the 'year' column to datetime onjects and store them in a new column 'datetime'.
6. Replace NaN in table with None.

Please see the [Python script]({link to Python script on Github}) for more details on this processing.

You can view the processed {Resource Watch public title} dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/com_039_rw0_agricultural_trade_statistics.zip), or [from the source website](https://www.fao.org/faostat/en/#data/TCL).

###### Note: This dataset processing was done by [Alex Sweeney](https://github.com/alxswny) and [Chris Rowe](https://www.wri.org/profile/chris-rowe), and QC'd by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou).
