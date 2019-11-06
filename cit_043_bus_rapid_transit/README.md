## Global Bus Rapid Transit Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Bus Rapid Transit](https://brtdata.org/indicators/systems/year_system_commenced) for [display on Resource Watch](https://resourcewatch.org/data/explore/Cities-with-Bus-Rapid-Transit).

The Global Bus Rapid Transit (BRT) dataset includes the name of the BRT system, the year it commenced, the location of the BRT (city and region), and the source. Each of these values are provided for BRT systems launched between 1986 and 2019. 

While this dataset be viewed on the source website, it is not directly downloadable there. In order to display the BRT data on Resource Watch, the dataset was copied from the source website and joined with the city centroid coordinates from [Natural Earth's Populated Places dataset](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-populated-places/) for mapping purposes. 

Below, we describe the actions taken to upload the dataset and join it to city coordinates:
1. Copy and paste the data table from the source website into Excel. Upload this Excel spreadsheet to Carto as a table named "cit_043_bus_rapid_transit."
2. Join the Global Bus Rapid Transit data (“cit_043_bus_rapid_transit”) with the Populated Places dataset ("city_centroid"), which had previously been uploaded to the Resource Watch Carto account. These tables should be joined on the “city” column in each dataset, using the following SQL statement:
```
SELECT city_centroid.city, cit_043_cities_with_bus_rapid_transit.city, city_centroid.the_geom, 
cit_043_cities_with_bus_rapid_transit.source, cit_043_cities_with_bus_rapid_transit.value, 
cit_043_cities_with_bus_rapid_transit.country

FROM "wri-rw".city_centroid

INNER JOIN cit_043_cities_with_bus_rapid_transit ON city_centroid.city = cit_043_cities_with_bus_rapid_transit.city
```
You can view the processed Global Bus Rapid Transit (BRT) dataset [on Resource Watch](https://resourcewatch.org/data/explore/Cities-with-Bus-Rapid-Transit).

You can also access the original dataset [on the source website](https://brtdata.org/indicators/systems/year_system_commenced).

###### Note: This dataset processing was done by [Ken Wakabayashi](https://www.wri.org/profile/ken-wakabayashi), and QC'd by [Liz Saccoccia](https://www.wri.org/profile/liz-saccoccia).
