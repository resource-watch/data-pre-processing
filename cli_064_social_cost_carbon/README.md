## Country-Level Social Cost of Carbon Dataset Pre-processing
This file describes the data pre-processing that was done to [Country-level Social Cost of Carbon dataset](https://www.nature.com/articles/s41558-018-0282-y.epdf?author_access_token=XLBRLEGdT_Kv0n8_OnvpedRgN0jAjWel9jnR3ZoTv0Ms70oz073vBeHQkQJXsJbey6vjdAHHSPxkHEN8nflPeQI6U86-MxWO1T1uUiSvN2A-srp5G9s7YwGWt6-cuKn2e83mvZEpXG3r-J0nv0gYuA%3D%3D) for [display on Resource Watch]().

This dataset was provided by the source as a csv file in a GitHub repository. The data is stored in the csv file named "cscc_db_v2.csv" in the [Github repository](https://github.com/country-level-scc/cscc-database-2018) for the 2018 Country-level Social Cost of Carbon (CSCC) Database.

This table was read into Python as a dataframe. The data was trimmed, the column for country code was renamed and the the table was converted from wide to a long form so that the final table contains a single column of CSCC percentiles and a single column of CSCC scores.

Please see the [Python script](https://github.com/Taufiq06/data-pre-processing/blob/master/cli.064_social_cost_carbon/cli.064_social_cost_carbon_processing.py) for more details on this processing.

You can view the processed Country-Level Social Cost of Carbon dataset [on Resource Watch]().

You can also download original dataset [directly through Resource Watch](), or [from the source website](https://github.com/country-level-scc/cscc-database-2018/blob/master/cscc_db_v2.csv).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
