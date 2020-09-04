## Projected Sea Level Rise Dataset Pre-processing
This file describes the data pre-processing that was done to the [Total Ensemble Mean Sea Surface Height Time Series](https://icdc.cen.uni-hamburg.de/en/ar5-slr.html) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

This dataset is provided by the source as a single NetCDF file. The following variables are shown on Resource Watch:
- 2010 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2010, relative to the average sea surface height during 1986–2005
- 2020 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2020, relative to the average sea surface height during 1986–2005
- 2030 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2030, relative to the average sea surface height during 1986–2005
- 2040 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2040, relative to the average sea surface height during 1986–2005
- 2050 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2050, relative to the average sea surface height during 1986–2005
- 2060 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2060, relative to the average sea surface height during 1986–2005
- 2070 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2070, relative to the average sea surface height during 1986–2005
- 2080 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2080, relative to the average sea surface height during 1986–2005
- 2090 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2090, relative to the average sea surface height during 1986–2005
- 2100 Cumulative Sea Level Rise (m): Projected mean sea surface height in 2100, relative to the average sea surface height during 1986–2005

To display these data on Resource Watch, a multiband GeoTIFF file was extracted from one subdataset within the source NetCDF file, with each band in the resulting GeoTIFF corresponding to one year in the time series. This GeoTIFF was then translated into the appropriate coordinates for web display.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ocn_003_projected_sea_level_rise/ocn_003_projected_sea_level_rise_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/).

You can also download the original dataset [from the source website](https://icdc.cen.uni-hamburg.de/en/ar5-slr.html).

###### Note: This dataset processing was done by [Peter Kerins](https://www.wri.org/profile/peter-kerins).