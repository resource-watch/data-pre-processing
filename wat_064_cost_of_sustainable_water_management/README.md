## Cost of Sustainable Water Management Dataset Pre-processing
This file describes the data pre-processing that was done to the [Achieving Abundance: Understanding the Cost of a Sustainable Water Future dataset](https://www.wri.org/resources/data-sets/achieving-abundance) for [display on Resource Watch](https://resourcewatch.org/data/explore/wat064-Cost-of-Sustainable-Water-Management).

This dataset was provided by the source as a csv file. It included the estimated cost of delivering sustainable water management to each country by 2030, along with the cost associated with each aspect of sustainable water management.

Each aspect of sustainable water management was given as a percent of total estimated cost. The percentages were proivded by the source in decimal form (0-1). These were multiplied by 100 and rounded to the nearest integer to provide percentages between 0 and 100.

Below, are the steps used to process the dataset before displaying on Resource Watch:

1. Upload the Achieving Abundance dataset to Carto in a table named wat_064_sdg6_investment.
2. Add new columns to the table to store each sustainable water management category percentage (on the 0-100 scale) using the following SQL statement:
```
ALTER TABLE "wri-rw".wat_064_sdg6_investment
    ADD drinking_water _percent numeric,
    ADD access_to_sanitation_percent numeric,
    ADD industrial_pollution_percent numeric,
    ADD agricultural_pollution_percent numeric,
    ADD water_scarcity_percent numeric,
    ADD water_management_percent numeric;
```
3.  Populate these new columns by converting each sustainable water management category to rounded percents using the following SQL statement:
```
UPDATE "wri-rw".wat_064_sdg6_investment

SET access_to_drinking_water_percent = round(access_to_drinking_water*100),
access_to_sanitation_percent = round(access_to_sanitation*100), industrial_pollution_percent = round(industrial_pollution*100), agricultural_pollution_percent = round(agricultural_pollution*100), water_scarcity_percent = round(water_scarcity*100),
water_management_percent = round(water_management*100);
```

You can view the processed, Cost of Sustainable Water Management dataset [here](https://wri-rw.carto.com/tables/wat_064_sdg6_investment/public).

You can also download original dataset [from the source website](https://www.wri.org/resources/data-sets/achieving-abundance).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
