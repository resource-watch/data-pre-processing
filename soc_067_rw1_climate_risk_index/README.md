## Climate Risk Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Climate Risk Index 2020](https://germanwatch.org/en/17307) for [display on Resource Watch](https://resourcewatch.org/data/explore/7e98607d-23d8-42f8-9662-5658f349bf0f).

The source provided the data as a table in a pdf file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe.
2. Rename column headers to be more descriptive and to remove special characters so that it can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/master/soc_067_rw1_climate_risk_index) for more details on this processing.

You can view the processed Climate Risk Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/7e98607d-23d8-42f8-9662-5658f349bf0f).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_067_rw1_climate_risk_index.zip), or [from the source website](https://germanwatch.org/en/cri).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
