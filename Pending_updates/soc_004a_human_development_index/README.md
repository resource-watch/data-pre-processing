## Human Development Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Human Development Index (HDI)](http://hdr.undp.org/en/2016-report) for [display on Resource Watch](https://resourcewatch.org/data/explore/bea122ce-1e4b-465d-8b7b-fa11aadd20f7).

The source provided the data in a .xlsx format.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe.
2. Remove rows containing metadata (headers, sub-sections names, footnotes, etc.).
3. Name columns based on the year, title, and unit provided in the metadata.
3. Replace ".." with None.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_004a_human_development_index/soc_004a_human_development_index_processing.py) for more details on this processing.

You can view the processed Human Development Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/bea122ce-1e4b-465d-8b7b-fa11aadd20f7).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](http://hdr.undp.org/en/data#).

###### Note: This dataset processing was done by Matthew Iceland and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
