## Municipal Waste Dataset Pre-processing
This file describes the data pre-processing that was done to [the Municipal Waste Generated per Capita](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW) for [display on Resource Watch](https://resourcewatch.org/data/explore/10337db6-8321-445e-a60b-28fc1e114f29).

The source provided the data as a csv file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe and remove the duplicated column 'YEA'. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_029_municipal_waste/cit_029_municipal_waste_processing.py) for more details on this processing.

You can view the processed Municipal Waste dataset [on Resource Watch](https://resourcewatch.org/data/explore/10337db6-8321-445e-a60b-28fc1e114f29).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://stats.oecd.org/Index.aspx?DataSetCode=MUNW).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
