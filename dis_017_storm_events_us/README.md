This file describes the data pre-processing that was done to [the Storm Events in the US dataset)](https://www.ncdc.noaa.gov/stormevents/ftp.jsp) for display on Resource Watch as the following datasets:
- [Tornadoes in the U.S.](https://resourcewatch.org/embed/widget/8a0f738e-4fb9-4a4c-8b9a-6363f619cdd5).
- [Hail in the U.S.](https://resourcewatch.org/embed/widget/355f550b-ea6d-418d-b89d-5fbd58f3ba1b)

The source provided this dataset as a set of annual csv files that were accessed via [ftp](ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/). For each year, three csvs were available: the "details" csv (files starting with "StormEvents_details"), the "fatalities" csv (files starting with "StormEvents_fatalities"), and the "locations" csv (files starting with "StormEvents_locations"). The "details" and "locations" csvs for all of the years available were used.

Below, we describe the steps used to append and merge the csv files:
1. The "locations" and "details" csv files for each year available were downloaded using the FTP library.
2. The annual files were appended so that there were two tables containing all of the years of data available: one table for the "details" and one for the "locations". Whitespaces in the appended locations table were deleted.
3. The "details" and the "locations" tables were merged based on the column "event_id". 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/dis_017_storm_events_us/dis_017_storm_events_us_processing.py) for more details on this processing.

You can view the processed datasets on Resource Watch:
- [Tornadoes in the U.S.](https://resourcewatch.org/embed/widget/8a0f738e-4fb9-4a4c-8b9a-6363f619cdd5).
- [Hail in the U.S.](https://resourcewatch.org/embed/widget/355f550b-ea6d-418d-b89d-5fbd58f3ba1b)

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/dis_017_storm_events_us.zip), or [from the source website](https://www.ncdc.noaa.gov/stormevents/ftp.jsp).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).

