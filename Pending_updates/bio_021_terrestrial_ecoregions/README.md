## {Terrestrial Ecoregions} Dataset Pre-processing
This file describes the data pre-processing that was done to [the Terrestrial Ecoregions](http://maps.tnc.org/files/metadata/TerrEcos.xml) for [display on Resource Watch](https://resourcewatch.org/data/explore/d9034fa9-8db0-4d52-b018-46fae37d3136).

The source provided the data as a shapefile.

Below, we describe the steps used to reformat the shapefile to upload it to Carto.

1. Read in the polygon shapefile as a geopandas data frame.
2. Project the data so its coordinate system is WGS84.
3. Convert the geometries of the data from shapely objects to geojsons.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/bio_021_terrestrial_ecoregions/bio_021_terrestrial_ecoregions_processing.py) for more details on this processing.

You can view the processed Terrestrial Ecoregions dataset [on Resource Watch](https://resourcewatch.org/data/explore/d9034fa9-8db0-4d52-b018-46fae37d3136).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://geospatial.tnc.org/datasets/7b7fb9d945544d41b3e7a91494c42930_0).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
