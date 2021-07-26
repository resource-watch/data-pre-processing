## Gender Gap Index Dataset Pre-processing
This file describes the data pre-processing that was done to the [Gender Gap Index](http://www3.weforum.org/docs/WEF_GGGR_2021.pdf) for [display on Resource Watch](https://resourcewatch.org/data/explore/).

The source provides the data in a pdf that is reformated into a table. Below, we describe the steps used to download the Global Gender Gap index and four subindices from the pdf and upload the reformated table to Carto.

1. Read in the necessary tables from the WEF pdf using the tabula-py module.
2. Create a dictionary: keys are each year of data downloaded, values are the dataframes corresponding to each year.
3. The first dataframe pulled using Tabula is the main Global Gender Gap Index, but is split into two sets of columns. The two sets of columns are then concatenated for each year, and a new column is created for year.
4. The next two dataframes contain the four subindicies. Each dataframe contains two indicies, with each index split into two sets of columns. The two sets of columns are then concatenated for each year, and a new column is created for year.
5. For each year of data pulled, the main index and subindicies are merged by ['year', 'country'].
6. This dataframe is then appended to the Carto table 


Please see the [Python script](https://github.com/resource-watch/data-pre-processing/tree/soc_026_rw0_global_gender_gap/soc_026_rw0_global_gender_gap.py) for more details on this processing.

You can view the processed Gender Gap Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/Gender-Gap-Index-2?section=All+data&selectedCollection=&zoom=4.644176750750855&lat=6.019854545136706&lng=-21.499869732141935&pitch=0&bearing=0&basemap=dark&labels=light&layers=%255B%257B%2522dataset%2522%253A%25220be2ce12-79b3-434b-b557-d6ea92d787fe%2522%252C%2522opacity%2522%253A1%252C%2522layer%2522%253A%2522c50a39b7-c72e-4e41-a92d-e49ec28e441c%2522%257D%255D&aoi=&page=1&sort=relevance&sortDirection=-1&search=wef).

You can also download the original dataset [from the source website](https://www.weforum.org/reports/the-global-gender-gap-report-2021).

###### Note: This dataset processing was done by [{Jason Winik}](https://www.wri.org/profile/jason-winik), and QC'd by [{name}]({link to WRI bio page}).
