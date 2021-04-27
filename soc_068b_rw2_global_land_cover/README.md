## Global Land Cover (IPCC Classification) Dataset Pre-processing
This file describes the data pre-processing that was done to [Land Cover Maps - v2.1.1](https://cds.climate.copernicus.eu/cdsapp#!/dataset/satellite-land-cover?tab=overview) for [display on Resource Watch](https://resourcewatch.org/data/explore/0851d568-0960-4e21-b954-0d4f9d8854f9).

Each year of data is provided by the source as a NetCDF file within a zipped folder. In order to display this data on Resource Watch, the lccs-class variable in each NetCDF was converted to a GeoTIFF.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_068b_rw2_global_land_cover/soc_068b_rw2_global_land_cover_processing.py) for more details on this processing.

You can view the processed Global Land Cover (IPCC Classification) dataset [on Resource Watch](https://resourcewatch.org/data/explore/0851d568-0960-4e21-b954-0d4f9d8854f9).

You can also download the original dataset [from the source website](http://maps.elie.ucl.ac.be/CCI/viewer/).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
