# FISHING EMPLOYMENT
This file describes the data pre-processing that was done to the [Labor Forece Statistics on Employment by Sex and Economic Activity (ISIC Level 1 and 2)](https://ilostat.ilo.org/data/#) for displaying the Fishing Employment dataset [on Resource Watch](LINK).

The source provided two datasets, one for ISIC Level 1 classificaltions and one for ISIC Level 2 classifications, as two zipped CSV files (csv.gz) files.

Below we describe the main steps taken to process the data and combine the two files to upload the data to Carto. The purpose of this processing is to creat a table that can be used to display the proportion of Fishing Sector Employment out of Total Naturl Sector Employment (Agriculture, hunting, forestry, and fishing).  Each dataset contains data categorized by both ISIC Revolution 3.1 (before 2007) and 4 (after 2007).At classfiication Level 1, in the Revolution 3.1 of the classifciation system the Natural Sector Economic Activity was split into two classifications (A. Agriculture, hunting and forestry [ECO_ISIC3_A] and B. Fishing [ECO_ISIC3_B]) which are aggregated to get the total Natural Sector Employment.


1. For each dataset, manually download the dataset as a .gz files from https://ilostat.ilo.org/data/#, unzip the file, move to the appropriate directory, and read the csv as a pandas data frame.
2. Rename the 'time' column to 'year'.
3. Rename the 'ref_area' column to 'area'.
4. Filter the data to the appropriate classification depending on the revolution of the classification system (Level 1 - 'ECO_ISIC3_A','ECO_ISIC3_B', 'ECO_ISIC4_A'; Level 2 - 'EC2_ISIC3_B05'. 'EC2_ISIC4_A03').
5. For Level 1 data, group the 'ECO_ISIC3_A' and 'ECO_ISIC3_B'by area, year, and sex and aggregate the rows by summing the obs_value column.
6. Add a 'level' column to reflect the level of the data (ISIC Level 1 or ISIC Level 2).
7. Add a 'type' column to reflect the type of observed value (Natural Sector Total Employment or Fishing Sector Employment).
8. Add a 'rev' column to reflect the classification system (Rev 3 or Rev 4).
9. Add the suffix '_natural' or 'fish' to columns from the respective datasets that will be duplicated when merged.
10. Merge the processed data frames. 
11. Convert 'year' column to date time object.
12. Sort the new data frame by country and year and reorder the columns.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_037_rw0_fishing_employment/com_037_rw0_fishing_employment_processing.py) for more details on this processing.

You can view the processed dataset for [display on Resource Watch](LINK).

You can also download the original dataset [directly through Resource Watch](https://wri-public-data.s3.amazonaws.com/resourcewatch/com_037_rw0_fishing_employment.zip), or [from the source website](https://ilostat.ilo.org/data/#).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Yujing Wu](https://www.wri.org/profile/Yuging-Wu).
