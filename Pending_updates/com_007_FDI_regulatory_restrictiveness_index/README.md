## FDI Regulatory Restrictiveness Index Dataset Pre-processing
This file describes the data pre-processing that was done to [the OECD FDI Regulatory Restrictiveness Index](http://www.oecd.org/investment/fdiindex.htm) for [display on Resource Watch](https://resourcewatch.org/data/explore/fe311144-8c0e-4440-b068-6efd057e0f6a).

The source provided the data in a csv format.

Below, we describe the steps used to reformat the table so that it is formatted correctly to upload to Carto.

1. Read the data as a pandas dataframe.
2. Remove the column 'TIME' since it is a duplicate of the column 'Year'.
3. Remove the column 'Flag Codes' and 'Flags' since they don't contain any value.
4. Remove the column 'Type of restriction', 'SERIES', 'Series', and 'RESTYPE' since they only contain one unique value.
5. Remove the column 'SECTOR' since it contains the same information as the column 'Sector / Industry'.
6. Convert the format of the data frame from long to wide so each sector will have its own column.

Please see the [Python script](https://github.com/resource-watch/data-pre-processing/blob/master/com_007_FDI_regulatory_restrictiveness_Index/com_007_FDI_regulatory_restrictiveness_Index_processing.py) for more details on this processing.

You can view the processed FDI Regulatory Restrictiveness Index dataset [on Resource Watch](https://resourcewatch.org/data/explore/fe311144-8c0e-4440-b068-6efd057e0f6a).

You can also download the original dataset [directly through Resource Watch]({s3 link if available}), or [from the source website](http://stats.oecd.org/Index.aspx?datasetcode=FDIINDEX#).

###### Note: This dataset processing was done by [Yujing Wu](https://www.wri.org/profile/yujing-wu), and QC'd by [Amelia Snyder](https://www.wri.org/profile/amelia-snyder).
