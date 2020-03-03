## Cost of Sustainable Water Management Dataset Pre-processing
This file describes the data pre-processing that was done to the [Achieving Abundance: Understanding the Cost of a Sustainable Water Future dataset](https://www.wri.org/resources/data-sets/achieving-abundance) for [display on Resource Watch](https://resourcewatch.org/data/explore/wat064-Cost-of-Sustainable-Water-Management).

This dataset was provided by the source as a excel file. It included the estimated cost of delivering sustainable water management to each country by 2030, along with the cost associated with each aspect of sustainable water management.

This table was read into Python as a dataframe and went through some preprocessing steps. Below, are the steps used to process the dataset before displaying on Resource Watch:

1. Add new columns to the table to store each sustainable water management category percentage (on the 0-100 scale).
2. Populate these new columns by converting each aspect of sustainable water management to a percent of total estimated cost.
3. These were multiplied by 100 and rounded to the nearest integer to provide percentages between 0 and 100.
4. Upload the processed dataset to Carto in a table named wat_064_cost_of_sustainable_water_management_edit.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/taufiq/wat_064_cost_of_sustainable_water_management/wat_064_cost_of_sustainable_water_management_processing.py) for more details on this processing.

You can view the processed, Cost of Sustainable Water Management dataset [here](https://wri-rw.carto.com/tables/wat_064_cost_of_sustainable_water_management_edit/public).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/wat_064_cost_of_sustainable_water_management_edit.zip), or [from the source website](https://www.wri.org/resources/data-sets/achieving-abundance).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
