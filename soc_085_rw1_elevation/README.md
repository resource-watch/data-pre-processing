## Elevation Dataset Pre-processing
This file describes the data pre-processing that was done to [the Advanced Land Observing Satellite (ALOS) Global Digital Surface Model (DSM) 30 m, Version 3.2](https://www.eorc.jaxa.jp/ALOS/en/aw3d30/aw3d30v3.2_product_e_e1.2.pdf) for [display on Resource Watch](https://resourcewatch.org/data/explore/cef9d930-61c3-4641-87b1-9f3072210d84).

The source provided the data as a Google Earth Engine image collection. Each image in the collection is a 1°x1° tile. The tiles were mosaicked together to create a global dataset for display on Resource Watch.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/soc_085_rw1_elevation/soc_085_rw1_elevation_processing.py) for more details on this processing.

You can view the processed Elevation dataset [on Resource Watch](https://resourcewatch.org/data/explore/cef9d930-61c3-4641-87b1-9f3072210d84).

You can also download the original dataset [from the source website](https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D30_V3_2).

###### Note: This dataset processing was done by [Weiqi Zhou](https://www.wri.org/profile/weiqi-zhou), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
