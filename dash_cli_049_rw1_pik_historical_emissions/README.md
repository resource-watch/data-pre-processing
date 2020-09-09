## PIK Historical Emissions Dataset Pre-processing
This file describes the data pre-processing that was done to [the PRIMAP-hist dataset](https://www.climatewatchdata.org/data-explorer/historical-emissions?historical-emissions-data-sources=pik&historical-emissions-end_year=2017&historical-emissions-gases=ch4%2Cco2%2Cn2o%2Cf-gas&historical-emissions-regions=All%20Selected&historical-emissions-sectors=All%20Selected&historical-emissions-start_year=1850&page=1&sort_col=sector&sort_dir=ASC#meta) for [display on Resource Watch]({link to dataset's metadata page on Resource Watch}).

Climate Watch provides the data as a csv file within a zipped folder.

Below, we describe the steps used to reformat the data before we upload it to Carto.

1. Read in the data as a pandas data frame.
2. Subset the dataframe to select the rows containing global GHG emission information.
3. The source provides the data with each row representing a country and each year of data stored in a different column. This is considered to be "wide" form. We converted each of those files from wide form to long form, in which there is one column that indicates the year and one column that indicates the value for that year.
4. Rename the 'variable', 'value', and 'Data source' columns to be 'datetime', 'yr_data', and 'source'.
5. Convert the year values in the 'datetime' column to be datetime objects.
6. Drop the column 'unit'.
7. Sum all types of greenhouse gas emissions for each sector every year.
8. Add a column 'gas' to indicate the values in the 'yr_data' column indicate the total emissions of all greenhouse gases.
9. Add a column 'gwp' to indicate the type of global warming potential standard used in the calculation of greenhouse gas emissions.
10. Reorder the columns in the dataframe.
11. Convert the column names to be in lowercase letters.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/dash_cli_049_rw1_pik_historical_emissions/dash_cli_049_rw1_pik_historical_emissions_processing.py) for more details on this processing.

You can view the processed PIK Historical Emissions dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://www.climatewatchdata.org/data-explorer/historical-emissions?historical-emissions-data-sources=cait&historical-emissions-gases=all-ghg&historical-emissions-regions=All%20Selected&historical-emissions-sectors=total-including-lucf&page=1#data).

###### Note: This dataset processing was done by [Daniel Gonzalez](https://www.wri.org/profile/daniel-gonzalez) and [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
