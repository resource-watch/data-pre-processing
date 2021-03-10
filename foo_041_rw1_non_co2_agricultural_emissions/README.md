This file describes the data pre-processing that was done to [Non-CO₂ Agricultural Emissions](http://www.fao.org/faostat/en/#data/GT) for [display on Resource Watch](https://bit.ly/3aUxqvK).

The source provided this dataset as a CSV file within a zip folder.

Below we describe the main steps taken to process the data so that it is formatted correctly to be uploaded to Carto.

1. Read in the data as a pandas dataframe and subset the dataframe to select the total emissions of the agriculture sector. 
2. Subset the dataframe to obtain emission values in carbon dioxide equivalent.
3. Convert the emission values from gigagrams to gigatonnes and store them in a new column 'value_gigatonnes'.
4. Rename the 'Value' column to 'value_gigagrams'.
5. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
6. Convert column names to lowercase and replace spaces with underscores to match Carto column name requirements.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_041_rw1_non_co2_agricultural_emissions/foo_041_rw1_non_co2_agricultural_emissions_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3aUxqvK).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_041_rw1_non_co2_agricultural_emissions.zip), or [from the source website](http://www.fao.org/faostat/en/#data/GT).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
