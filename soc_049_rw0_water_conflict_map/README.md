## Water Conflict Map Dataset Pre-processing
This file describes the data pre-processing that was done to [the World Water Conflict Chronology Map](https://www.worldwater.org/water-conflict/ ) for [display on Resource Watch](https://resourcewatch.org/data/explore/24928aa3-28d3-457c-ad2a-62f3c83ef663).

The source provided the data as a PHP file.

Below, we describe the steps used to reformat the table to upload it to Carto.

1. Rename the 'Start' and 'End' columns to 'start_year' and 'end_year' since 'end' is a reserved word in PostgreSQL.
2. Convert the start and end year of the conflicts to datetime objects using first day of January to fill day and month for each conflict and store them in two new columns 'start_dt' and 'end_dt'. 
3. Convert column headers to lowercase and replace spaces within them with underscores so that the table can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_049_rw0_water_conflict_map/soc_049_rw0_water_conflict_map_processing.py) for more details on this processing.

You can view the processed Water Conflict Map dataset [on Resource Watch](https://resourcewatch.org/data/explore/24928aa3-28d3-457c-ad2a-62f3c83ef663).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_049_rw0_water_conflict_map.zip), or [from the source website](https://www.worldwater.org/water-conflict/).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
