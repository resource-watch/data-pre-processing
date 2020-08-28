## Political Rights and Civil Liberties Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Freedom in the World: The Annual Survey of Political Rights and Civil Liberties](https://freedomhouse.org/report-types/freedom-world) for [display on Resource Watch](https://resourcewatch.org/data/explore/a7067e9f-fe40-4338-85da-13a6071c76fe).

The source provided the data in an excel format.

In order to process this data for display on Resource Watch, the data was read into python as a pandas dataframe and the empty columns within the dataframe were removed.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_005a_political_rights_civil_liberties_index/soc_005a_political_rights_civil_liberties_index_processing.py) for more details on this processing.

You can view the processed Political Rights and Civil Liberties Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/a7067e9f-fe40-4338-85da-13a6071c76fe).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://freedomhouse.org/report/freedom-world/2020/leaderless-struggle-democracy).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
