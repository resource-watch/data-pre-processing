# Fragile States Index Dataset Pre-processing
This file describes the data pre-processing that was done to [Fragile States Index](https://fragilestatesindex.org/) for [display on Resource Watch](https://bit.ly/2O6Qv4F).

The source provided this dataset as a set of excel files, each containing data for a different year.

The excel files were concatenated into a sole pandas dataframe. Column headers were renamed to remove special characters and spaces so that the table can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_023_rw1_fragile_states_index/soc_023_rw1_fragile_states_index_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/2O6Qv4F).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_023_rw1_fragile_states_index.zip), or [from the source website](https://fragilestatesindex.org/excel/).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
