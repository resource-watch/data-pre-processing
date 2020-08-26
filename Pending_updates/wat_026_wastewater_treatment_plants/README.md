## Wastewater Treatment Plants (U.S.) Dataset Pre-processing
This file describes the data pre-processing that was done to [the Environmental Protection Agency (EPA) Facility Registry Service (FRS): Wastewater Treatment Plants](https://catalog.data.gov/dataset/epa-facility-registry-service-frs-wastewater-treatment-plants) for [display on Resource Watch](https://resourcewatch.org/data/explore/371e700e-bc9a-4526-af92-335d888de309).

The source provided the data as a shapefile.

Below, we describe the steps used to reformat the shapefile to upload it to Carto}.

1. Read in the shapefile as a geopandas data frame.
2. Project the data so its coordinate system is WGS84.
3. Convert the data type of the column 'REGISTRY_I' to integer.
3. Convert the geometries of the data from shapely objects to geojsons.
4. Create a new column from the index of the dataframe to use as a unique id column (cartodb_id) in Carto.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/wat_026_wastewater_treatment_plants/wat_026_wastewater_treatment_plants_processing.py) for more details on this processing.

You can view the processed Wastewater Treatment Plants (U.S.) dataset [on Resource Watch](https://resourcewatch.org/data/explore/371e700e-bc9a-4526-af92-335d888de309).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://hifld-geoplatform.opendata.arcgis.com/datasets/environmental-protection-agency-epa-facility-registry-service-frs-wastewater-treatment-plants/data).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
