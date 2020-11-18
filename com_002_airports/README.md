## Airports Dataset Pre-processing
This file describes the data pre-processing that was done to [the Airports dataset](https://openflights.org/data.html) for [display on Resource Watch](https://resourcewatch.org/data/explore/c111725c-e1c5-467b-a367-742db1c70893).

The source provided the data in a dat format.

Below, we describe the steps used to reformat the table before we uploaded it to Carto.

1. Read in the data as a pandas data frame and remove the extra column containing indexes.
2. Reorder the index and give the columns the correct header.
3. Replace '\N' and 'NaN' in the data frame with None.
4. Change the data types of the 'latitude', 'longitude', and 'daylight_savings_time' columns to float.
5. Change the data types of the 'altitude' column to integer.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_002_airports/com_002_airports_processing.py) for more details on this processing.

You can view the processed Airports dataset [on Resource Watch](https://resourcewatch.org/data/explore/c111725c-e1c5-467b-a367-742db1c70893).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/com_002_airports.zip), or [from the source website](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
