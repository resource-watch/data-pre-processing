## Gender Development Index Dataset Pre-processing
This file describes the data pre-processing that was done to [Gender Development Index (GDI)](http://hdr.undp.org/en/content/gender-development-index-gdi) for [display on Resource Watch](https://bit.ly/3ks6hUb).

The source provided this dataset as a csv file accessed through its [website](http://hdr.undp.org/en/indicators/137906#). 

Below, we describe the main actions performed to process the csv file:
1. Convert the dataframe from wide form to long form, in which one column indicates the year.
2. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
3. Rename column headers to remove special characters and spaces so that the table can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_002_rw1_gender_development_index/soc_002_rw1_gender_development_index_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3ks6hUb).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_002_rw1_gender_development_index.zip), or [from the source website](http://hdr.undp.org/en/indicators/137906#).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
