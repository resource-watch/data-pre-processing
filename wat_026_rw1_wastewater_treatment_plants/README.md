## Wastewater Treatment Plants (U.S.) Dataset Pre-processing
This file describes the data pre-processing that was done to [the Environmental Protection Agency (EPA) Facility Registry Service (FRS): Wastewater Treatment Plants](https://catalog.data.gov/dataset/epa-facility-registry-service-frs-wastewater-treatment-plants) for [display on Resource Watch](https://resourcewatch.org/data/explore/a8581e62-63dd-4973-bb2a-b29552ad9e37).

The source provided the data as a table within a geodatabase.

Below, we describe the steps used to reformat the table to upload it to Carto.

1. Read in the table as a geopandas data frame.
2. Convert the column names to lowercase.
3. Convert the data type of the column 'registry_id' to integer.
4. Project the data so its coordinate system is WGS84.
5. Create 'latitude' and 'longitude' columns based on the 'geometry' column of the geopandas dataframe.
6. Drop the 'geometry' column from the geopandas dataframe.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/wat_026_rw1_wastewater_treatment_plants/wat_026_rw1_wastewater_treatment_plants_processing.py) for more details on this processing.

You can view the processed Wastewater Treatment Plants (U.S.) dataset [on Resource Watch](https://resourcewatch.org/data/explore/a8581e62-63dd-4973-bb2a-b29552ad9e37).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/wat_026_rw1_wastewater_treatment_plants.zip), or [from the source website](https://hifld-geoplatform.opendata.arcgis.com/datasets/environmental-protection-agency-epa-facility-registry-service-frs-wastewater-treatment-plants/data).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
