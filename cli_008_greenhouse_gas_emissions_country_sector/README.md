## Greenhouse Gas Emissions by Country and Economic Sector Dataset Pre-processing
This file describes the data pre-processing that was done to [Greenhouse Gas Emissions by Country and Economic Sector](https://www.climatewatchdata.org/data-explorer) for [display on Resource Watch](https://bit.ly/39sQ4ds).

The source provided this dataset as a csv file accessed through its [data explorer](https://www.climatewatchdata.org/data-explorer). The following options were selected from the dropdown menu:
1. Data source: CAIT
2. Countries and regions: All selected
3. Sectors: All selected
4. Gases: All GHG
5. Start year: 1990
6. End year: 2018

Below, we describe the main actions performed to process the csv file:
1. Import the data as a pandas dataframe.
2. Convert the dataframe from wide form to long form, in which one column indicates the year and the other columns indicate the emission values for the year.
3. Convert the table from long to wide form, in which the emission values of each sector are stored in individual columns. 
4. Convert years in the 'year' column to datetime objects and store them in a new column 'datetime'.
5. Rename column headers to be more descriptive and to remove special characters so that it can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cli_008_greenhouse_gas_emissions_country_sector/cli_008_greenhouse_gas_emissions_country_sector_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/39sQ4ds).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/cli_008_greenhouse_gas_emissions_country_sector.zip), or [from the source website](https://www.climatewatchdata.org/data-explorer).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
