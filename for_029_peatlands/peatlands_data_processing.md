
## This file describes the data pre-processing that was done to create the dataset Peatlands


The Peatlands dataset comes in zipped files per continent: Africa, Asia, Europe, North America, Oceania, and South America. For some continents, shapefiles are provided at a finer level such as at the national level. For example, North America includes Canada, the United States, and Other North American peatlands.

Below is the list of steps used to process and combine regional datasets into a global peatlands dataset.

1. Upload individual regional datasets to Carto
2. Add a column called region and name it after the shapefile region name. For example, these statements were used for Southeast Asia peatlands shapefile which I called for_029_peatland_sea.

```
ALTER TABLE for_029_peatland_sea ADD COLUMN region VARCHAR

UPDATE for_029_peatland_sea

SET region = 'Southeast Asia'’;
```
3. Examine attribute columns and standardize area column names. Some shapefiles have an area column named “peat_area” and some have columns named “area”. The following statement was used to standardize the area column name.  
```
ALTER TABLE for_029_peatland_africa
RENAME peat_area TO area;
```
4. Combine individual regional shapefile into a global peatlands dataset which I called for_029_peatlands with the following statement. 
```
INSERT INTO for_029_peatlands(the_geom,  area, region) SELECT the_geom,  area, region
FROM for_029_peatland_sea
```
View global peatland dataset [here](https://resourcewatch.carto.com/u/wri-rw/dataset/for_029_peatlands)

Download original dataset [here](http://wri-public-data.s3.amazonaws.com/resourcewatch/for_029_peatlands.zip), or [here](http://archive.researchdata.leeds.ac.uk/251/)
