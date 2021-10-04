This file describes the data pre-processing that was done to Global Food Product Import Shares and Global Food Product Export Shares datasets for [display on Resource Watch](https://resourcewatch.org/).

The source provided this dataset as excel files accessed through its [data explorer](https://wits.worldbank.org).

Data for imports can be downloaded with the following link:
https://wits.worldbank.org/CountryProfile/en/Country/WLD/StartYear/1988/EndYear/2019/TradeFlow/Export/Indicator/XPRT-PRDCT-SHR/Partner/ALL/Product/16-24_FoodProd
Data for exports can be downloaded with the following link:
https://wits.worldbank.org/CountryProfile/en/Country/WLD/StartYear/1988/EndYear/2019/TradeFlow/Import/Indicator/MPRT-PRDCT-SHR/Partner/ALL/Product/16-24_FoodProd#

The following options were selected from the source website dropdown menu:
1. Country/region: World
2. Year: 1988-2019
3. Trade flow: Import/Export
4. Indicators: Import Product share(%)/Export Product share(%)
5. View By: Product
6. Product: Food Products
7. Partner: By country and region

Below, we describe the main actions performed to process the excel files:
1. Import the data as a pandas dataframe.
2. Convert the dataframe from wide form to long form, in which one column indicates the year and the other columns indicate the percentage of imports or exports related to food products for the year.
3. Convert years in the 'year' column to datetime objects and store them in a new column 'datetime'.
4. Rename column headers to be more descriptive and to remove special characters so that it can be uploaded to Carto without losing information.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/foo_066_rw0_food_product_shares/foo_066_rw0_food_product_shares.py) for more details on this processing.

You can also download the original datasets [from the source website](https://wits.worldbank.org).

###### Note: This dataset processing was done by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes), and QC'd by [Eduardo Castillero Reyes](https://wrimexico.org/profile/eduardo-castillero-reyes).
