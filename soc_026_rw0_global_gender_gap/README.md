## Gender Gap Index Dataset Pre-processing
This file describes the data pre-processing that was done to the [Gender Gap Index](http://www3.weforum.org/docs/WEF_GGGR_2021.pdf) for [display on Resource Watch](https://resourcewatch.org/data/explore/0be2ce12-79b3-434b-b557-d6ea92d787fe).

The source provides the data in a pdf that is reformated into a table. Below, we describe the steps used to download the Global Gender Gap index and four subindices from the pdf and upload the reformated table to Carto.

1. Read in the data tables for the global gender gap index and its four subindices from the Global Gender Gap Report pdf using the tabula-py module. Both the 2020 and 2021 datasets were pulled in.
2. Transform the data for each index/subindex into a pandas dataframe.
3. A year column was added to all dataframes to indicate the year of the report.
4. Country names were processed to fix inconsistencies in naming.
5. Dataframes containing the main index and subindicies were merged into one table using the columns 'year' and 'country'.
6. This dataframe was then appended to the existing data we had previously processed by reading in the existing Carto table as a dataframe and concatenating it with the new data.


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/soc_026_rw0_global_gender_gap/soc_026_rw0_global_gender_gap.py) for more details on this processing.

You can view the processed Gender Gap Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/0be2ce12-79b3-434b-b557-d6ea92d787fe).

You can also download the original dataset [from the source website](https://www.weforum.org/reports/the-global-gender-gap-report-2021).

###### Note: This dataset processing was done by [Jason Winik](https://www.wri.org/profile/jason-winik), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
