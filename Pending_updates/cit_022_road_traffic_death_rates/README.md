## Road Traffic Death Rates Dataset Pre-processing
This file describes the data pre-processing that was done to [the Road Traffic Deaths dataset](http://apps.who.int/gho/data/node.wrapper.imr?x-id=198) for [display on Resource Watch](https://resourcewatch.org/data/explore/6b670396-c52c-430c-b5bb-20693da03b60).

The source provided the dataset as a csv file.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto. 
1. Read in the data as a pandas dataframe and rename all the columns.
2. We split the 'estimated_number_of_road_traffic_deaths_data' column and stored the lower and upper bound of the estimates in two new columns.
3. We added a column for datetime with January 1, 2016 for every row.
4. We reordered the columns.
5. We removed all the spaces within numbers in the 'estimated_number_of_road_traffic_deaths_data' column.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/cit_022_road_traffic_death_rates/cit_022a_road_traffic_death_rates_processing.py) for more details on this processing.

You can view the processed Road Traffic Death Rates dataset [on Resource Watch](https://resourcewatch.org/data/explore/6b670396-c52c-430c-b5bb-20693da03b60).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](http://apps.who.int/gho/data/node.main.A997?lang=en).

###### Note: This dataset processing was done by [Taufiq Rashid](https://www.wri.org/profile/taufiq-rashid), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
