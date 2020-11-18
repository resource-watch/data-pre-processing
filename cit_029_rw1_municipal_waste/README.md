## Municipal Waste Dataset Pre-processing
This file describes the data pre-processing that was done to [the Municipal Waste Generated per Capita](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW) for [display on Resource Watch](https://resourcewatch.org/data/explore/23f41bb2-2312-41ab-aaf2-ef584f80b31a).

The source provided the data as a csv file.

Below, we describe the steps used to reformat the table to upload it to Carto.

1. Read in the csv file as a pandas dataframe.
2. Subset the dataframe based on the 'Variable' column to obtain municipal waste generated per capita for each country.
3. The columns 'YEA' and 'Year' are identical, so the 'YEA' column was removed.
4. Convert the column names to lowercase and replace the spaces with underscores.
5. Convert the years in the 'year' column to datetime objects and store them in a new column 'datetime'.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_029_rw1_municipal_waste/cit_029_rw1_municipal_waste_processing.py) for more details on this processing.

You can view the processed Municipal Waste dataset [on Resource Watch](https://resourcewatch.org/data/explore/23f41bb2-2312-41ab-aaf2-ef584f80b31a).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/cit_029_rw1_municipal_waste.zip), or [from the source website](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
