## Index of Coastal Protection by Coral Reefs Dataset Pre-processing
This file describes the data pre-processing that was done to the [Global Coral Protection Index](http://maps.oceanwealth.org/) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The dataset is contained within a GeoDataBase, containing many vector layers, many of which are available for viewing on the Mapping Ocean Wealth platform. The following variable is shown on Resource Watch:
- 2014 Relative Value of Coral Reef Shoreline Protection: Relative value of protection against waves provided to coastlines by coral reefs through reduction of wave height and wave energy, estimated as a function of exposed populations and infrastructure receiving some protection.

To process this data for display on Resource Watch, the GeoDataBase was downloaded, and the layer of interest was extracted into a shapefile. The appropriate decile attribute was then rasterized into a single-band GeoTIFF, which geospatial properties identical to the originating vector file.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_014_index_of_coastal_protection_by_coral_reefs/ocn_014_index_of_coastal_protection_by_coral_reefs.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The original data can be viewed on the [Mapping Ocean Wealth platform](http://maps.oceanwealth.org/), and are available for download upon request.

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).