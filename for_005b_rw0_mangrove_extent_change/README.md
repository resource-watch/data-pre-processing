## Mangrove Extent Change Data Pre-Processing
This file describes the data pre-processing that was done to [Global Mangrove Watch (1996-2016)](https://data.unep-wcmc.org/datasets/45) for [display on Resource Watch](https://resourcewatch.org/data/explore/f31dece0-9256-428a-84de-3a59f5c06bb7).

This dataset was provided by the source as two shapefiles, one for 1996 and one for 2016.

To calculate the mangrove extent change from 1996 to 2016 for display on Resource Watch, the following steps were performed in Esri Modelbuilder in ArcMap:

1. Open the shapefiles as layers in ArcMap.
2. Convert the 1996 and 2016 layers to Lambert (a cylindrical equal area) projection (8287).
3. Calculate the geometric intersection of the 1996 and 2016 layers.
4. Erase the geometric intersection from the 1996 layer to create a loss layer.
5. Erase the geometric intersection from the 2016 layer to create a gain layer.
6. Merge the gain and loss layers. 
7. Export the merged layer as a shapefile.

You can view the processed dataset for [display on Resource Watch](https://resourcewatch.org/data/explore/f31dece0-9256-428a-84de-3a59f5c06bb7).

You can also download original underlying datasets [from the source website](https://data.unep-wcmc.org/datasets/45).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by []().
