## Social Institutions and Gender Index Dataset Pre-processing
This file describes the data pre-processing that was done to [Social Institutions and Gender Index](https://stats.oecd.org/Index.aspx?DataSetCode=GIDDB2019#) for [display on Resource Watch](https://bit.ly/3ejWtuc).

The source provided this dataset as a csv file accessed through its [website](https://stats.oecd.org/Index.aspx?DataSetCode=GIDDB2019#). 

Below, we describe the main actions performed to process the csv file:
1. Convert the dataframe from long to wide form, converting the variables into columns.
2. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
3. Drop rows for data aggregated by region or income group (labeled 'all regions' or 'all income groups') so that only disaggregated data remains and data is not duplicated.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_045_rw1_women_political_representation/soc_045_rw1_women_political_representation_processing.py) for more details on this processing.

You can view the processed Women's Political Representation dataset [on Resource Watch](https://bit.ly/3ejWtuc).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_002_rw1_gender_development_index.zip), or [from the source website](https://stats.oecd.org/Index.aspx?DataSetCode=GIDDB2019).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
