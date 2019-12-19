## Batch Upload of World Bank Datasets
This file describes the data upload process used in this docker container to upload a number of datasets from the [World Bank API](https://data.worldbank.org/) to [Resource Watch](resourcewatch.org).

On Resource Watch we host numerous datasets from the World Bank, which are all available through their API in a standard format. For example see the [Unemployment Rate page](https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD). We use this script to update all of our World Bank datasets at once.
1. We first set up a table of the dataset names, Carto table names, and corresponding World Bank indicator codes. Each dataset on the World Bank API has a unique indicator code, for example the [Unemployment Rate page](https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD) indicator code is NY.GDP.MKTP.PP.CD, and can be found at the end of the URL.
2. Then for each dataset we download the dataset from the World Bank API
3. We then remove areas defined by the World Bank such as "European Union" and match every country name and ISO code to the Resource Watch standard names.
4. We then upload the reformatted table to our Carto account.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/upload_worldbank_data/contents/main.py) for more details on this processing.

###### Note: This dataset processing was done by [Kristine Lister](https://www.wri.org/profile/kristine-lister), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
