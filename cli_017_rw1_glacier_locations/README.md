## {Resource Watch Public Title} Dataset Pre-processing
This file describes the data pre-processing that was done to [the Glacier Locations](http://glims.colorado.edu/glacierdata/) for [display on Resource Watch](https://resourcewatch.org/data/explore/cli017-Glacier-Extents_replacement?section=All+data&selectedCollection=&zoom=3&lat=0&lng=0&pitch=0&bearing=0&basemap=dark&labels=light&layers=%255B%257B%2522dataset%2522%253A%2522ad218d82-058b-4b8e-b790-44fb6d4b531f%2522%252C%2522opacity%2522%253A1%252C%2522layer%2522%253A%25221ab0f13b-b3cf-46fb-add5-2b802df9a9eb%2522%257D%255D&aoi=&page=1&sort=most-viewed&sortDirection=-1&topics=%255B%2522glacier%2522%255D).

The source provided the two shapefiles in a zipped folder. 

1. Glims Glacier Locations (points)
2. Glims Glaceir Extent (polygons)

Below, we describe the steps used to download the shapefiles and format them to upload to Carto.

1. Download the zipped folder and import the shapefiles as geopandas dataframes.
2. Rename columns to match Carto table and delete unnecessary columns.
3. Reuplod to Carto and Resource Watch.

```
Include any SQL or GEE code you used in a code snippet.
```

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/cli_017_rw1_glacier_locations/cli_017_rw1_glacier_locations) for more details on this processing.

You can view the processed Glacier Locations dataset [on Resource Watch](https://resourcewatch.org/data/explore/cli017-Glacier-Extents_replacement?section=All+data&selectedCollection=&zoom=3&lat=0&lng=0&pitch=0&bearing=0&basemap=dark&labels=light&layers=%255B%257B%2522dataset%2522%253A%2522ad218d82-058b-4b8e-b790-44fb6d4b531f%2522%252C%2522opacity%2522%253A1%252C%2522layer%2522%253A%25221ab0f13b-b3cf-46fb-add5-2b802df9a9eb%2522%257D%255D&aoi=&page=1&sort=most-viewed&sortDirection=-1&topics=%255B%2522glacier%2522%255D).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/cli_017_glacier_extent.zip), or [from the source website](http://www.glims.org/download/).

###### Note: This dataset processing was done by [Jason Winik](https://www.wri.org/profile/jason-winik), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
