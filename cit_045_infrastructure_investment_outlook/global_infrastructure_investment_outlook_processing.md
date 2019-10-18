## Infrastructure Investment Outlook Dataset Pre-processing
This file describes the data pre-processing that was done to [the Global Infrastructure Investment Outlook dataset](https://outlook.gihub.org/) for [display on Resource Watch](https://resourcewatch.org/data/explore/Infrastructure-Investment-Outlook).

The Global Infrastructure Investment Outlook data can be downloaded by country on the source website. The downloaded data includes the expected investment in infrastructure for that country (current trends), and well as the investment in infrastructure that would be needed to match the performance of other countries within the same income group (investment needs). Each of these values are provided for each year between 2006 and 2040.

Because we wanted to display the data on Resource Watch for all countries, a complete dataset that included all countries was requested from the data provider, rather than processing the data individually for each country.

Below, we describe the calculations that were done to the global dataset in Microsoft Excel to produce the data shown on Resource Watch.

The global dataset that was provided included two spreadsheets: one for investment needs and one for current trends.  Within each sheet, each row represented a particular country, and each column represented a single year. 

The Pivot Tables feature in Excel was used to combine the two sheets into one by creating a new column called “investment_path” that indicated whether the data was a "current trend" or an "investment need."
 
The infrastructure investment gap for each year was be calculated from this data by finding the the difference between the "current trend" value and the "investment need" value for each country and each year.

The Pivot Tables feature was used again to create a new column called “year” so that all years of data could be stored stored in a single column called "value," rather than storing each year's data in a unique column. The “value” column was also divided by 1,000,000 to show the value in millions of USD, which was stored in a new “value_millions_” column.  

The total infrastructure investment gap for a country, which is shown on Resource Watch, is the sum of the infrastructure investment gap for all years between 2016 and 2040. This selection of years was used to be consistent with how the source calculated the total infrastructure investment gap displayed on their website.


You can view the processed infrastructure investment outlook dataset [on Resource Watch](https://resourcewatch.org/data/explore/Infrastructure-Investment-Outlook).

You can also download original dataset [from the source website](https://outlook.gihub.org/).

###### Note: This dataset processing was done by [Ken Wakabayashi](https://www.wri.org/profile/ken-wakabayashi), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
