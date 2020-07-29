## Historical Cyclone Intensity Dataset Pre-processing
This file describes the data pre-processing that was done to the [Tropical cyclones wind speed buffers footprint 1970-2009](https://preview.grid.unep.ch/index.php?preview=data&events=cyclones&evcat=4&lang=eng) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is provided by the source as a (zipped) GeoTIFF file. The following variables are shown on Resource Watch:
- 1970-2009 Maximum Storm Intensity (cy_intensity): Highest estimated category on the Saffir-Simpson hurricane wind scale, which measures storm intensity, during 1970-2009.

Because the data were already provided in a compatible format and projection, very little processing was necessary to display this data on Resource Watch.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_005_historical_cyclone_intensity/ocn_005_historical_cyclone_intensity_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original dataset [from the source website](https://preview.grid.unep.ch/index.php?preview=data&events=cyclones&evcat=4&lang=eng).

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).