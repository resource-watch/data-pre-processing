## Gender Inequality Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Gender Inequality Index]({learn more link}) for [display on Resource Watch](https://resourcewatch.org/data/explore/soc025-Gender-Inequality-Index).

The original data is downloadable in a .xlsx format.  

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to carto.  We read in the data as a pandas dataframe, deleted columns and rows without data, and renamed the columns.  Then we converted the '..' to 'None'.  

Please see the [Python script]({link to Python script on Github}) for more details on this processing.

You can view the processed Gender Inequality Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/soc025-Gender-Inequality-Index).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/soc_025a_gender_inequality_index.zip), or [from the source website](http://hdr.undp.org/en/content/table-5-gender-inequality-index-gii).

###### Note: This dataset processing was done by [Liz Saccoccia](https://www.wri.org/profile/liz-saccoccia), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
