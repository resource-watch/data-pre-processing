## Water Conflict Map Dataset Pre-processing
This file describes the data pre-processing that was done to [the World Water Conflict Chronology Map](https://www.worldwater.org/water-conflict/ ) for [display on Resource Watch](https://resourcewatch.org/data/explore/24928aa3-28d3-457c-ad2a-62f3c83ef663).

The source provided the data as a PHP file.

The 'Start' and 'End' columns were renamed to be 'start_year' and 'end_year' since 'end' is a reserved word in PostgreSQL. The start and end year of the conflicts were converted to datetime objects (using first day of January to fill day and month for each conflict) and stored in two new columns 'start_dt' and 'end_dt'. The 'Conflict Type' column was renamed to be 'conflict_type'. The resulting table was uploaded to Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_049_rw0_water_conflict_map/soc_049_rw0_water_conflict_map_processing.py) for more details on this processing.

You can view the processed Water Conflict Map dataset [on Resource Watch](https://resourcewatch.org/data/explore/24928aa3-28d3-457c-ad2a-62f3c83ef663).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_049_rw0_water_conflict_map.zip), or [from the source website](https://www.worldwater.org/water-conflict/).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu)., and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
