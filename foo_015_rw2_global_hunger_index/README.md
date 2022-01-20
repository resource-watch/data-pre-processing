## Global Hunger Index Dataset Pre-processing
This file describes the data pre-processing that was done to [2021 Global Hunger Index dataset](https://www.globalhungerindex.org/download/all.html) for [display on Resource Watch](https://resourcewatch.org/data/explore/c37b0b21-3d11-46ea-ba5d-4be4c0caa8ae).

This dataset was provided by the source as a excel. The data shown on Resource Watch can be found in TABLE 1.1 Global Hunger Index Scores By 2021 GHI Rank.

This table was read into Python as a dataframe. The data was cleaned, values listed as '<5' were replaced with 5, and the the table was converted from wide to a long form.

Countries with incomplete data but significant cause for concern were not included in the source's data table, but they were noted [by the source](https://www.globalhungerindex.org/designations.html). A new column was added to the table to store a flag for "Incomplete data, significant concern," and rows were added to the table for each of these countries noted by the source. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_015_rw2_global_hunger_index/foo_015_rw2_global_hunger_index_processing.py) for more details on this processing.

You can view the processed Global Hunger Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/c37b0b21-3d11-46ea-ba5d-4be4c0caa8ae).

You can also download original dataset [directly through Resource Watch](http://wri-projects.s3.amazonaws.com/resourcewatch/foo_015_rw2_global_hunger_index_edit.zip), or [from the source website](https://www.globalhungerindex.org/download/all.html).

###### Note: This dataset processing was done by [Tina Huang](https://www.wri.org/profile/tina-huang), and QC'd by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou).
