## Recycled Waste Dataset Pre-processing
This file describes the data pre-processing that was done to [the Recovered Waste: Recycled](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW) for [display on Resource Watch](https://resourcewatch.org/data/explore/46e7870a-5590-42c7-bf5b-56c7def7399b).

The data source provided the dataset as one csv file. 

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Import the data as a pandas dataframe.
2. Subset the dataframe based on the 'Variable' column to obtain recycling waste for each country.
3. Remove column 'VAR' since it contains the same information as the column 'Variable'.
4. Remove column 'YEA' since it contains the same information as the column 'Year'.
5. Remove column 'Unit Code' since it contains the same information as the column 'Unit'.
6. Remove column 'Flag Codes' since it contains the same information as the column 'Flags'.
7. Remove column 'Reference Period Code' and 'Reference Period' since they are all NaNs.
8. Replace NaN in the table with None.
9. Convert years in the 'year' column to datetime objects and store them in a new column 'datetime'.
10. Replace whitespaces in column names with underscores and convert the column names to lowercase to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_015_rw1_recycling_rates/com_015_rw1_recycling_rates_processing.py) for more details on this processing.

You can view the processed Effect of Agricultural Policies on Commodity Prices dataset [on Resource Watch](https://resourcewatch.org/data/explore/46e7870a-5590-42c7-bf5b-56c7def7399b).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/com_015_rw1_recycling_rates.zip), or [from the source website](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
