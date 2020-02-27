## Cost of Sustainable Water Management Dataset Pre-processing
This file describes the data pre-processing that was done to the [Achieving Abundance: Understanding the Cost of a Sustainable Water Future dataset](https://www.wri.org/resources/data-sets/achieving-abundance) for [display on Resource Watch](https://resourcewatch.org/data/explore/wat064-Cost-of-Sustainable-Water-Management).

This dataset was provided by the source as a csv file. It included the estimated cost of delivering sustainable water management to each countries by 2030 along with the cost associated with each aspect of sustainable water management. Each aspect of sustainable water management was given as a percent of total estimated cost. However, the percents were not given as actual percents. So, they were multiplied with 100 and rounded to the nearest integer. The dataset also contained the country code (ISO) for each country. This information was combined with World Resources Institute (WRI) base countries shape data so the dataset can be displayed on Resource Watch.

Below, are the steps used to preprcoess the dataset before displaying on Resource Watch:

1. Upload the Achieving Abundance dataset to Carto in a table named wat_064_sdg6_investment.
2. Add new columns to the table for each water categories and convert them to rounded percents using the following SQL statements:

```
ALTER TABLE "wri-rw".wat_064_sdg6_investment
    ADD drinking_water _percent numeric,
    ADD access_to_sanitation_percent numeric,
    ADD industrial_pollution_percent numeric,
    ADD agricultural_pollution_percent numeric,
    ADD water_scarcity_percent numeric,
    ADD water_management_percent numeric;

UPDATE "wri-rw".wat_064_sdg6_investment
	SET access_to_drinking_water_percent = round(access_to_drinking_water*100), access_to_sanitation_percent = round(access_to_sanitation*100), industrial_pollution_percent = round(industrial_pollution*100), agricultural_pollution_percent = round(agricultural_pollution*100), water_scarcity_percent = round(water_scarcity*100), water_management_percent = round(water_management*100);
```
3. Attach WRI shapes data to each rows in the table using the country code (ISO) from source data. The following SQL statement was used to standardize the area column name:
```
SELECT wri.cartodb_id, ST_Transform(wri.the_geom, 3857) AS 
the_geom_webmercator, wri.name, data.country, data.total_cost 
FROM wat_064_sdg6_investment data 
LEFT OUTER JOIN wri_countries_a wri ON data.iso = wri.iso_a3 
WHERE total_cost IS NOT NULL 
AND wri.name IS NOT NULL
```

You can view the processed, Cost of Sustainable Water Management dataset [here](https://wri-rw.carto.com/tables/wat_064_sdg6_investment/public).

You can also download original dataset [from the source website](https://www.wri.org/resources/data-sets/achieving-abundance).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
