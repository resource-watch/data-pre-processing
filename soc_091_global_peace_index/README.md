## Global Peace Index Dataset Pre-processing
This file describes the data pre-processing that was done to [Global Peace Index 2019 dataset](http://visionofhumanity.org/app/uploads/2020/02/GPI-2019-overall-scores-2008-2019.xlsx) for [display on Resource Watch](https://resourcewatch.org/data/explore/soc091-Global-Peace-Index).

This dataset was provided by the source as a pdf report. The data shown on Resource Watch can be found in Table 2.1 Global Hunger Index Scores By 2019 GHI Rank, which is on page 17 of the report.

This table was read into Python as a dataframe. The data was cleaned, values listed as '<5' were replaced with 5, and the the table was converted from wide to a long form.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_091_global_peace_index/soc_091_global_peace_index_processing.py) for more details on this processing.

You can view the processed Global Hunger Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/soc091-Global-Peace-Index).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/soc_091_global_peace_index.zip), or [from the source website](http://visionofhumanity.org/app/uploads/2020/02/GPI-2019-overall-scores-2008-2019.xlsx).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
