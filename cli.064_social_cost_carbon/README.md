## Country-Level Social Cost of Carbon Dataset Pre-processing
This file describes the data pre-processing that was done to [Country-level social cost of carbon dataset](https://github.com/country-level-scc/cscc-database-2018/blob/master/cscc_db_v2.csv) for [display on Resource Watch]().

This dataset was provided by the source as a csv file in a GitHub repositury. The data shown on Resource Watch can be found in database of "Country-level social cost of carbon", which is the csv file "cscc_db_v2.csv" in the Github repository.

This table was read into Python as a dataframe. The data was trimmed, the column for country code was renamed and the the table was converted from wide to a long form so that the final table contains a single column of cscc percentile and a single column of cscc scores.

Please see the [Python script](https://github.com/Taufiq06/data-pre-processing/blob/master/cli.064_social_cost_carbon/cli.064_social_cost_carbon.py) for more details on this processing.

You can view the processed Country-Level Social Cost of Carbon dataset [on Resource Watch]().

You can also download original dataset [directly through Resource Watch](), or [from the source website](https://github.com/country-level-scc/cscc-database-2018/blob/master/cscc_db_v2.csv).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
