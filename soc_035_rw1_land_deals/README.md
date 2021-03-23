This file describes the data pre-processing that was done to [Land Deals](https://landmatrix.org/) for [display on Resource Watch](https://bit.ly/3vTNI0u).

The source provided this dataset as a xlsx file accessed through its [data explorer](https://landmatrix.org/list/deals/). The following options were selected from the dropdown menu:
1. Deal size: 200 hectares
2. Negotiation status: Concluded

Below, we describe the main actions performed to process the xlsx file:
1. Selected only a subset of the columns displayed by the source
2. Created column "negotiation_status_year" by extracting the year from the "negotiation status" column, then it was converted to a datetime column. 
3. Rename column headers and remove special characters so that it can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cli_008a_greenhouse_gas_emissions_country_sector/cli_008a_greenhouse_gas_emissions_country_sector_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3vTNI0u).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/soc_035_rw1_land_deals.zip), or [from the source website](https://landmatrix.org/).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by ?????.
