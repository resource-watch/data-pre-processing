## Projected Coral Bleaching Dataset Pre-processing
This file describes the data pre-processing that was done to the [Downscaled climate model projections of coral bleaching condition](https://coralreefwatch.noaa.gov/climate/projections/downscaled_bleaching_4km/index.php) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is contained within an ArcGIS Layer Package file (and available for viewing in Google Earth via a Keyhole Marukup Language zip archive). The following variables are shown on Resource Watch:
- Onset of 2x per Decade Severe Coral Bleaching Conditions (per_decade_2x): First year when severe bleaching conditions are projected to occur at least twice per decade. These projections correspond to the RCP 8.5 "business as usual" scenario, under which current emissions trends continue.
- Onset of 10x per Decade Severe Coral Bleaching Conditions (per_decade_10x): First year when severe bleaching conditions are projected to occur at least ten times per decade. These projections correspond to the RCP 8.5 "business as usual" scenario, under which current emissions trends continue.

To process this data for display on Resource Watch, the ArcGIS Layer Package was downloaded, and its components were saved as GeoTIFFs. The relevant GeoTIFFs were merged into a single multi-band GeoTIFF, with separate bands containing the data for each variable.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_010_projected_coral_bleaching/ocn_010_projected_coral_bleaching_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original data [from the source website](https://coralreefwatch.noaa.gov/climate/projections/downscaled_bleaching_4km/index.php).

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).