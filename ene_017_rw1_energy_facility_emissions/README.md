This file describes the data pre-processing that was done to [Energy Facility Emissions (US)](https://ghgdata.epa.gov/ghgp/main.do#) for [display on Resource Watch](https://bit.ly/3kNAD3i).

The source provided this dataset as an xls file accessed through its [website](https://ghgdata.epa.gov/ghgp/main.do#). To access the file select the "Export Data" option and then select "All Reporting Years". 

Below, we describe the main actions performed to process the xls file:

1. Convert the years in the 'Year' column to datetime objects and store them in a new column 'datetime'.
2. Rename column headers to remove special characters and spaces so that the table can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/ene_017_rw1_energy_facility_emissions/ene_017_rw1_energy_facility_emissions_processing.py) for more details on this processing.

You can view the processed Energy Facility Emissions (U.S.) dataset for [on Resource Watch](https://bit.ly/3kNAD3i).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/ene_017_rw1_energy_facility_emissions.zip), or [from the source website](https://ghgdata.epa.gov/ghgp/main.do#).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
