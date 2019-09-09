
## This file describes the data pre-processing that was done to create the dataset Peatlands


The Peatlands dataset comes in zipped files for each of the following continents: Africa, Asia, Europe, North America, Oceania, and South America. For some continents, a single shapefile was provided for the entire continent. For others, several shapefiles at a finer level, such as at the national level, were provided. For example, the zipped file for North America includes shapefiles for Canada, the United States, and other North American peatlands.

Below, we describe the steps used to process and combine these regional datasets into a global peatlands dataset.

1. Upload individual regional shapefile datasets to Carto.
2. For each regional dataset in Carto, add a column called "region", and fill it with the name of the shapefile region. For example, the following SQL statements were used for Southeast Asia peatlands shapefile, which was stored in a table named for_029_peatland_sea:

```
ALTER TABLE for_029_peatland_sea ADD COLUMN region VARCHAR

UPDATE for_029_peatland_sea

SET region = 'Southeast Asia';
```
3. Examine attribute columns and standardize area column names. Some shapefiles have an area column named “peat_area” and some have columns named “area”. The following SQL statement was used to standardize the area column name:
```
ALTER TABLE for_029_peatland_africa
RENAME peat_area TO area;
```
4. Combine regional shapefiles into a global peatlands dataset, called for_029_peatlands. For example, the following SQL statement was used to insert the Southeast Asia peatlands shapefile into the new, global table: 
```
INSERT INTO for_029_peatlands(the_geom,  area, region) SELECT the_geom,  area, region
FROM for_029_peatland_sea
```
You can view the processed, global peatland dataset [here](https://resourcewatch.carto.com/u/wri-rw/dataset/for_029_peatlands).

You can also download original dataset, by region, [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/for_029_peatlands.zip), or [from the source website](http://archive.researchdata.leeds.ac.uk/251/).

###### Note: This dataset processing was done by [Tina Huang](https://www.wri.org/profile/tina-huang), and QC'ed by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
