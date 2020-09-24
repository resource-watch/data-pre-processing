## Major Ports Dataset Pre-processing
This file describes the data pre-processing that was done to [the World Port Index](https://msi.nga.mil/Publications/WPI) for [display on Resource Watch](https://resourcewatch.org/data/explore/28d1f505-571c-4a52-8215-48ea02aa4928).

The data source provided the dataset as one shapefile and one csv file. The csv file was used and its column names were converted to lowercase before we uploaded it to Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_017_rw2_major_ports/com_017_rw2_major_ports_processing.py) for more details on this processing.

You can view the processed Major Ports dataset [on Resource Watch](https://resourcewatch.org/data/explore/28d1f505-571c-4a52-8215-48ea02aa4928).

You can also download the original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/com_017_rw2_major_ports.zip), or [from the source website](https://msi.nga.mil/Publications/WPI).

###### Note: This dataset processing was done by [Matthew Iceland](https://github.com/miceland2) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
