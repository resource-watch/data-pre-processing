## Reservoirs and Dams Dataset Pre-processing
This file describes the data pre-processing that was done to [the GRanD, v1.3 dataset](http://globaldamwatch.org/grand/) for [display on Resource Watch](https://resourcewatch.org/data/explore/ene001a-Global-Reservoir-and-Dam-GRanD-v13).

This dataset comes in a zipped file containing two shapefiles - one containing the point locations of damns and the other containing polygons of reservoir areas.

Below, we describe the steps used to combine these two datasets into one data table on Carto.

1. Copy files associated with the reservoirs shapefile into a folder named grand_reservoirs_v1_3 and zip this file. Copy files associated with the dams shapefile into a folder named grand_dams_v1_3 and zip this file. Upload each of these shapefiles as a new table in Carto.
2. For each table in Carto, add a text column called "type" - for example, the reservoirs table was modified with the following SQL statement:
```
ALTER TABLE "wri-rw".grand_reservoirs_v1_3

ADD type text
```
3. Fill the "type" column with the type of data in the file (dam or reservoir). For the reservoirs table, the SQL statement would be:

```
UPDATE "wri-rw".grand_reservoirs_v1_3

SET type='reservoir'
```
4. Change the name of one table to fit standardized Resource Watch naming conventions. In this case, the grand_dams_v1_3 was renamed as ene_001a_grand_dams_and_reservoirs_v1_3.
5. Combine the reservoirs and dams tables into one with the following SQL statement:
```
INSERT INTO ene_001a_grand_dams_and_reservoirs_v1_3 

(the_geom, grand_id, res_name, dam_name, alt_name, river, alt_river, main_basin, sub_basin, near_city, 
alt_city, admin_unit, sec_admin, country, sec_cntry, year, alt_year, rem_year, dam_hgt_m, alt_hgt_m, 
dam_len_m, alt_len_m, area_skm, area_poly, area_rep, area_max, area_min, cap_mcm, cap_max, cap_rep, 
cap_min, depth_m, dis_avg_ls, dor_pc, elev_masl, catch_skm, catch_rep, data_info, use_irri, use_elec, 
use_supp, use_fcon, use_recr, use_navi, use_fish, use_pcon, use_live, use_othr, main_use, lake_ctrl, multi_dams, 
timeline, comments, url, quality, editor, long_dd, lat_dd, poly_src, type)

SELECT the_geom, grand_id, res_name, dam_name, alt_name, river, alt_river, main_basin, sub_basin, near_city, 
alt_city, admin_unit, sec_admin, country, sec_cntry, year, alt_year, rem_year, dam_hgt_m, alt_hgt_m, dam_len_m, 
alt_len_m, area_skm, area_poly, area_rep, area_max, area_min, cap_mcm, cap_max, cap_rep, cap_min, depth_m, 
dis_avg_ls, dor_pc, elev_masl, catch_skm, catch_rep, data_info, use_irri, use_elec, use_supp, use_fcon, use_recr, 
use_navi, use_fish, use_pcon, use_live, use_othr, main_use, lake_ctrl, multi_dams, timeline, comments, url, 
quality, editor, long_dd, lat_dd, poly_src, type 
 
FROM grand_reservoirs_v1_3
```
You can view the processed reservoirs and dams dataset [on Resource Watch](https://resourcewatch.org/data/explore/ene001a-Global-Reservoir-and-Dam-GRanD-v13).

You can also download original dataset [directly through Resource Watch](http://wri-public-data.s3.amazonaws.com/resourcewatch/ene_001a_reservoirs_and_dams.zip), or [from the source website](https://ln.sync.com/dl/bd47eb6b0/anhxaikr-62pmrgtq-k44xf84f-pyz4atkm/view/default/447819520013).

###### Note: This dataset processing was done by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
