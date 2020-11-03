## Bonn Challenge Restoration Commitment Dataset Pre-processing
This file describes the data pre-processing that was done to [the Bonn Challenge Restoration Commitment](http://www.bonnchallenge.org/) for [display on Resource Watch](https://resourcewatch.org/data/explore/fb5edc45-b105-4b13-a6c3-5f3e314a4086).

The source provided the data as a table on its website.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Create a new column 'unit' to store the unit of the pledged areas.
2. Remove 'hectare' from all the entries in the column 'pledged_area'.
3. Convert the data type of the 'pledged_area' column to integer.
4. Convert the values in the column 'pledged_area' to be in million hectares. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/for_018_rw1_bonn_challenge_restoration_commitment/for_018_rw1_bonn_challenge_restoration_commitment_processing.py) for more details on this processing.

You can view the processed Bonn Challenge Restoration Commitment dataset [on Resource Watch](https://resourcewatch.org/data/explore/fb5edc45-b105-4b13-a6c3-5f3e314a4086).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/for_018_rw1_bonn_challenge_restoration_commitment.zip), or [from the source website](https://www.bonnchallenge.org/pledges).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
