## Out-Of-School Rate Dataset Pre-processing
This file describes the data pre-processing that was done to [the Out-of-school Rate for Children, Adolescents and Youth of Primary, Lower Secondary and Upper Secondary School Age](http://data.uis.unesco.org/index.aspx) for [display on Resource Watch](https://resourcewatch.org/data/explore/b2483333-693a-44e2-ae00-47f21c6a00bd).

The data source provided the dataset as one csv file. 

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Import the data as a pandas dataframe.
2. Subset the dataframe based on the 'Indicator' column to obtain number of out-of-school children, adolescents and youth of primary and secondary school age for both sexes.
3. Subset the dataframe based on the 'LOCATION' column to only retain country-level data.
4. Remove column 'TIME' since it contains the same information as the column 'Time'.
5. Remove column 'Flag Codes' since it contains the same information as the column 'Flags'.
6. Replace NaN in the table with None.
7. Remove rows where the 'Value' column is None.
8. Remove data in 2020 since it only has data for one country.
9. Convert years in the 'Time' column to datetime objects and store them in a new column 'datetime'.
10. Convert the column names to lowercase to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_039_rw1_out_of_school_rate/soc_039_rw1_out_of_school_rate_processing.py) for more details on this processing.

You can view the processed Out-Of-School Rate dataset [on Resource Watch](https://resourcewatch.org/data/explore/b2483333-693a-44e2-ae00-47f21c6a00bd).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_039_rw1_out_of_school_rate.zip), or [from the source website](http://data.uis.unesco.org/index.aspx).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
