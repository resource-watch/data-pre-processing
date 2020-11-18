## Cost of Sustainable Water Management Dataset Pre-processing
This file describes the data pre-processing that was done to the [Achieving Abundance: Understanding the Cost of a Sustainable Water Future dataset](https://www.wri.org/resources/data-sets/achieving-abundance) for [display on Resource Watch](https://resourcewatch.org/data/explore/wat064-Cost-of-Sustainable-Water-Management).

This dataset was provided by the source as two excel files. Each file includes the estimated total cost of delivering sustainable water management by 2030, along with the breakdown of how that cost is distributed across different aspects of sustainable water management. One file shows these costs at the country level, and the other file shows the costs at a basin-level. Resource Watch displays the country-level data from this dataset.

The country-level spreadsheet was read into Python as a dataframe. New columns were added to show the percentage of the total cost that would come from each aspect. These columns were calculated by dividing the cost associated with each aspect of sustainable water management by the total cost, then multiplying them by 100. These percentages were rounded to the nearest integer.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/wat_064_cost_of_sustainable_water_management/wat_064_cost_of_sustainable_water_management_processing.py) for more details on this processing.

You can view the processed Cost of Sustainable Water Management dataset [on Resource Watch](https://resourcewatch.org/data/explore/wat064-Cost-of-Sustainable-Water-Management).

You can also download original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/wat_064_cost_of_sustainable_water_management.zip), or [from the source website](https://www.wri.org/resources/data-sets/achieving-abundance).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
