## Coral Reef Fisheries Relative Catch Pre-processing
This file describes the data pre-processing that was done to the [estimated relative coral reef-associated fisheries catch](http://maps.oceanwealth.org/) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The dataset is contained within a GeoDataBase, containing many vector layers, many of which are available for viewing on the Mapping Ocean Wealth platform. The following variable is shown on Resource Watch:
- Coral Reef Fisheries Catch: Estimate of the relative size of coral reef fisheries catch (by weight) grouped by decile, based on estimated reef productivity and fishing effort, as well as the presence of protected "no-take" fishing areas.

To process this data for display on Resource Watch, the GeoDataBase was downloaded, and the layer of interest was extracted into a shapefile. The appropriate decile attribute was then rasterized into a single-band GeoTIFF, which geospatial properties identical to the originating vector file.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_013_coral_reef_fisheries_relative_catch/ocn_013_coral_reef_fisheries_relative_catch.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The original data can be viewed on the [Mapping Ocean Wealth platform](http://maps.oceanwealth.org/), and are available for download upon request.

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).