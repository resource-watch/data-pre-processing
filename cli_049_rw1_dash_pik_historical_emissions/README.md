## PIK Historical Emissions Dataset Pre-processing
This file describes the data pre-processing that was done to [the PRIMAP-hist national historical emissions time series
(1850-2017)](https://dataservices.gfz-potsdam.de/pik/showshort.php?id=escidoc:4736895) for [display on Resource Watch]({link to dataset's metadata page on Resource Watch}).

The source provides the data as a csv file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read in the data as a pandas dataframe.
2. Subset the dataframe to obtain the aggregated emissions for all countries.
3. Subset the dataframe to obtain emissions of CH4, CO2, F Gases, and N2O.
4. Subset the dataframe to obtain GHG emissions that are primarily reported by countries.
5. Convert the dataframe from wide to long format so there will be one column indicating the year and another column indicating the emissions values.
6. Rename the 'variable' and 'value' columns created by the previous step to be 'year' and 'yr_data'.
7. Convert the emission values of CH4 and N2O to be in the unit of GgCO2eq using global warming potential in IPCC Fourth Assessment Report.
8. Convert the emission values to be in MtCO2eq.
9. Change 'GgCO2eq' to be 'MtCO2eq' in the 'unit' column .
10. Create a dictionary for all the major sectors and their corresponding codes in the dataframe based on the documentation at ftp://datapub.gfz-potsdam.de/download/10.5880.PIK.2019.018/PRIMAP-hist_v2.1_data-description.pdf.
11. Subset the dataframe to obtain the GHG emissions of the major sectors.
12. Convert the codes in the 'category' column to the sectors they represent.
13. Create a 'datetime' column to store the years as datetime objects and drop the 'year' column.
14. Sum the emissions of all types of GHG for each sector in each year.
15. Create a column 'source' to indicate the data source is PIK.
16. Create a 'gwp' column to indicate that the global warming potential used in the calculation is from the IPCC Fourth Assessment Report.
17. Create a 'gas' column to indicate that the emissions values are the sum of all GHG emissions.
18. Rename the 'category' column to 'sector'.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cli_049_rw1_dash_historical_emissions/cli_049_rw1_dash_historical_emissions_processing.py) for more details on this processing.

You can view the processed PIK Historical Emissions dataset [on Resource Watch]({link to dataset's metadata page on Resource Watch}).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](https://dataservices.gfz-potsdam.de/pik/showshort.php?id=escidoc:4736895).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu) and Daniel Gonzalez, and QC'd by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid).
