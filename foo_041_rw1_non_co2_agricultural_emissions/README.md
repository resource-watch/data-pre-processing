This file describes the data pre-processing that was done to [Non-CO₂ Agricultural Emissions](http://www.fao.org/faostat/en/#data/GT) for [display on Resource Watch](https://bit.ly/3aUxqvK).

The source provided this dataset as a csv file [data explorer](http://fenixservices.fao.org/faostat/static/bulkdownloads/Emissions_Agriculture_Agriculture_total_E_All_Data_(Normalized).zip
). 

Below we describe the main steps taken to process the file:

1. The file was filtered to only show the "Agriculture total" item.
2. The file was filtered to only show CO2eq emissions.
3. A column showing the conversion from gigagrams to gigatonnes was created.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_041_rw1_non_co2_agricultural_emissions/foo_041_rw1_non_co2_agricultural_emissions_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](https://bit.ly/3aUxqvK).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_041_rw1_non_co2_agricultural_emissions.zip), or [from the source website](https://wri-public-data.s3.amazonaws.com/resourcewatch/foo_041_rw1_non_co2_agricultural_emissions_edit.zip).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Yujing Wu](https://www.wri.org/profile/yujing-wu).
