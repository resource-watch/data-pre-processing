## Projected Ocean Acidification for Coral Reefs Dataset Pre-processing
This file describes the data pre-processing that was done to the [Projections of Coral Bleaching and Ocean Acidification for Coral Reef Areas](https://coralreefwatch.noaa.gov/climate/projections/piccc_oa_and_bleaching/index.php) to produce an dataset for use with coral reef content, and perhaps at some point [display on Resource Watch](https://resourcewatch.org/data/explore/). This is an alternate dataset to [the global version](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_006_projected_ocean_acidification/)

This dataset is contained within a NetCDF file. The following variable is shown on Resource Watch, with a separate layer for the projected value at the start of each decade between 2010 and 2100:
- 2XXX Aragonite Saturation State: Common measure of carbonate ion concentration, which indicates the availability of the calcium carbonate that is widely used by marine calcifiers, from lobsters to clams to starfish. For this dataset, that has been masked to include only areas containing coral reefs, according to the internal mask used by some datasets in the source package.

To process this data for display on Resource Watch, the NetCDF file was acquired directly from the source organization. The time series data were extracted to a multiband GeoTIFF, with one band for each year 2006-2100. This GeoTIFF was then masked (all bands), using other rasters within the source package to define the scope, in order to show projections only in pixels containing coral reefs. 

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_006alt_projected_ocean_acidification_coral_reefs/ocn_006alt_projected_ocean_acidification_coral_reefs.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download a representation of the data [from the source website](https://coralreefwatch.noaa.gov/climate/projections/piccc_oa_and_bleaching/index.php).

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).