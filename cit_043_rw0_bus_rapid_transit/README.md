This file describes the data pre-processing that was done to [Cities with Bus Rapid Transit](https://brtdata.org/indicators/systems/year_system_commenced) for [display on Resource Watch](https://bit.ly/3FGqorD).

The Global Bus Rapid Transit (BRT) dataset includes the name of the BRT system, the year it commenced, the location of the BRT (city and region), and the source. Each of these values are provided for BRT systems launched between 1968 and 2020.

While this dataset be viewed on the source website, it is not directly downloadable there. In order to display the BRT data on Resource Watch, the dataset was scraped from the source website and joined with the city centroid coordinates from [Natural Earth's Populated Places dataset](http://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/) for mapping purposes. Part of the scraping process was adapted from [Kiprono Elijah Koech article](https://towardsdatascience.com/web-scraping-scraping-table-data-1665b6b2271c).

Below, we describe the main actions performed to process the scraped html table:
1. Import the data as a pandas dataframe.
2. Drop the 'year' column and rename the 'value' column as 'year'.
3. Convert years in the new 'year' column to datetime objects and store them in a new column 'datetime'.
4. Change to lowercase the column headers and remove special characters from them.
5. Join the Global Bus Rapid Transit data (“cit_043_rw0_bus_rapid_transit”) with the Populated Places dataset ("ne_10m_populated_places_simple"), which had previously been uploaded to the Resource Watch Carto account. These tables should be joined on the “ne_10m_populated_places_simple.name” and "cit_043_rw0_bus_rapid_transit_edit.city" columns from the respective table, using the following SQL statement:

```
SELECT ne_10m_populated_places_simple.name, cit_043_rw0_bus_rapid_transit_edit.city,
ST_Transform(ne_10m_populated_places_simple.the_geom, 3857) AS the_geom_webmercator, cit_043_rw0_bus_rapid_transit_edit.source,
cit_043_rw0_bus_rapid_transit_edit.year, cit_043_rw0_bus_rapid_transit_edit.country 

FROM ne_10m_populated_places_simple

INNER JOIN cit_043_rw0_bus_rapid_transit_edit ON ne_10m_populated_places_simple.name = cit_043_rw0_bus_rapid_transit_edit.city
```

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_043_rw0_bus_rapid_transit/cit_043_rw0_bus_rapid_transit.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3FGqorD).

You can also download the data [from the source website](https://brtdata.org/indicators/systems/year_system_commenced).

###### ###### Note: This dataset processing and QC was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes).

