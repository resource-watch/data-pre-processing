This file describes the data pre-processing that was done to [the Storm Events in the US dataset)](https://www.ncdc.noaa.gov/stormevents/ftp.jsp) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The source provided this dataset as a set of annual csv files that were accessed via [ftp](ftp://ftp.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/). For each year, three csvs were available: the "details" csv (files starting with "StormEvents_details"), the "fatalities" csv (files starting with "StormEvents_fatalities"), and the "locations" csv (files starting with "StormEvents_locations"). The "details" and "locations" csvs for all of the years available were used.

Below, we describe the steps used to append and merge the csv files:
1.Download the data from 1950 to 2020 using the FTP library.
2.Appending the "details" and "locations" files and then merging them based on the column "event_id". Whitespaces in the appended locations file were deleted prior to merging.
3.Adding a point column based on the coordinates provided by the location file using geopandas.
