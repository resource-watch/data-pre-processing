## Total Suspended Matter Pre-processing
This file describes the data pre-processing that was done to the [total suspended matter concentration dataset](https://www.globcolour.info/CDR_Docs/GlobCOLOUR_PUG.pdf) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The dataset is available as a NetCDF, with a primary data layer and a secondary flags layer. Only the former is shown on Resource Watch:
- [Month Year] Total Suspended Matter Concentration (g/m³): The concentration of inorganic particulate matter in seawater. It is a measure of the turbidity of the water.

To process this data for display on Resource Watch, the NetCDF was downloaded, and the primary data layer was extracted into a single-band GeoTIFF.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_011_total_suspended_matter/ocn_011_total_suspended_matter_non-nrt.py) for more details on this processing.

You can view the processed dataset [on Resource Watch](https://resourcewatch.org/data/explore/).

The original dataset comes from [GlobColour](https://www.globcolour.info/products_description.html), an ESA Data User Element Project, and is freely accessible via FTP with registration.

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).