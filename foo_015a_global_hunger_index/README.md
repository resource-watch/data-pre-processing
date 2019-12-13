## Global Hunger Index Dataset Pre-processing
This file describes the data pre-processing that was done to [2019 Global Hunger Index dataset](https://www.globalhungerindex.org/download/all.html) for [display on Resource Watch](https://resourcewatch.org/data/explore/foo015a-Global-Hunger-Index).

This dataset was provided by the source as a pdf report. The data shown on Resource Watch can be found in Table 2.1 Global Hunger Index Scores By 2019 GHI Rank, which is on page 17 of the report.

This table was read into Python as a dataframe. The data was cleaned, values listed as '<5' were replaced with 5, and the the table was converted from wide to a long form.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_015a_global_hunger_index/foo_015a_global_hunger_index.py) for more details on this processing.

You can view the processed Global Hunger Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/foo015a-Global-Hunger-Index).

You can also download original dataset [directly through Resource Watch](http://wri-projects.s3.amazonaws.com/resourcewatch/foo_015a_global_hunger_index.zip), or [from the source website](https://www.globalhungerindex.org/download/all.html).

###### Note: This dataset processing was done by [Tina Huang](https://www.wri.org/profile/tina-huang), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
