## Standard Precipitation Index Data Retrieval
This file describes the process used to retrieve Standard Precipitation Index from the [the CHIRPS precipitation dataset](https://pubs.usgs.gov/ds/832/) for [display on Resource Watch](https://resourcewatch.org/data/explore/cli023-Standard-Precipitation-Index).

The Standard Precipitation Index dataset is calculated from CHIRPS precipitation data, using the [Climate Engine app](https://app.climateengine.org/climateEngine). Below, we list the parameters used in the Climate Engine app to produce and download the data shown on Resource Watch.

##### Variable
```
Type: Climate
Dataset: CHIRPS - Pentad
Variable: Standard Precipiation Index (SPI)
Computation Resolution (Scale): 4800 m (1/20-deg)
```
##### Processing
```
Statistic (over day range): No Statistic
Calculation: Standardized Index
```
##### Time Period
```
Season: Custom Date Range
Start Date: {YEAR}-01-01
End Date: {YEAR}-12-31
Year Range for Historical Avg/Distribution: 1981-2006
```
In the Time Period variables, above, the {YEAR} for Start Date and End Date should be replaced with the year for which you are currently pulling data.

The 'Get Map Layer' button was then used to produce a map of the Standard Precipitation Index data.

At the top of the page, the 'Download' tab was used to download the data for the following rectangular region:
```
NE corner: 50.0000N, 180.0000E
SW corner: -50.0000N, -180.0000E
```

You can view the processed, Standard Precipitation Index dataset [here](https://resourcewatch.org/data/explore/cli023-Standard-Precipitation-Index).

You can also download original dataset [from the source website](https://app.climateengine.org/climateEngine).

###### Note: This retrieval of this data was originally done by [Nathan Suberi](https://www.wri.org/profile/nathan-suberi). The retrieval process was documented by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
