This file describes the data pre-processing that was done to [Gender Development Index (GDI)](http://hdr.undp.org/en/content/gender-development-index-gdi) for [display on Resource Watch](https://bit.ly/3aszvip).

The source provided this dataset as a xlsx file accessed through its [website](http://hdr.undp.org/sites/default/files/2020_statistical_annex_table_4.xlsx). 

Below, we describe the main actions performed to process the xlsx file:
1. Skipping empty headers and footers. Also skipping other other descriptive rows inside the file (the name of the gender development group to which the countries are located into).
2. Change the country name to enable its merge with the contents of "wri_countries_a" carto table
3. Change special characters inside dataframe to None

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_002_gender_development_index/soc_002_gender_development_index_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3aszvip).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/soc_002_gender_development_index.zip), or [from the source website](http://hdr.undp.org/en/content/gender-development-index-gdi).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by ...
