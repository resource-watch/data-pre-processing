This file describes the data pre-processing that was done to [Storm Events in the US dataset)](https://www.ncdc.noaa.gov/stormevents/ftp.jsp) 

The source provided this dataset as a set of csv files, of which the "details" and "locations" files were used.

Below, we describe the steps used to append and merge the csv files:
1.Download the data from 1950 to 2020 using the FTP library.
2.Appending the "details" and "locations" files and then merging them based on the column "event_id". Whitespaces in the appended locations file were deleted prior to merging.
3.Adding a point column based on the coordinates provided by the location file using geopandas.

