## Coral Reef Tourism Value Dataset Pre-processing
This file describes the data pre-processing that was done to the [Mapped estimates of the dollar values of coral reefs to the tourism sector](http://maps.oceanwealth.org/) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The dataset is contained within a GeoDataBase, containing many vector layers, many of which are available for viewing on the Mapping Ocean Wealth platform. The following variables are shown on Resource Watch:
- Annual Value of Coral Reef Tourism (2013 USD/km²): Estimated total annual economic value per square kilometer of coral reefs to the tourism sector.
- Annual Value of On-Reef Coral Tourism (2013 USD/km²): Estimated annual economic value per square kilometer of on-reef activities to the tourism sector.
- Annual Value of Reef-Adjacent Coral Tourism (2013 USD/km²): Estimated annual economic value per square kilometer of reef-adjacent activities and services to the tourism sector.

To process this data for display on Resource Watch, the GeoDataBase was downloaded, and the layers of interest were extracted into individual shapefiles. Existing attributes were used to calculate a new attribute describe value per square kilometer. This attribute was then rasterized into a single-band GeoTIFF, which geospatial properties identical to the originating vector files. These GeoTIFF files were then merged into one multi-band GeoTIFF, with separate bands containing the data for each variable.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_012_coral_reef_tourism_value/ocn_012_coral_reef_tourism_value.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The original data can be viewed on the [Mapping Ocean Wealth platform](http://maps.oceanwealth.org/), and are available for download upon request.

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).
