## Trawling Dataset Pre-processing
This file describes the data pre-processing that was done to [Global Fishing Activity](https://globalfishingwatch.org/?utm_source=wri_map&utm_medium=api_integration&utm_campaign=ocean_watch) for [display on Resource Watch](https://resourcewatch.org/data/explore/6ccfb266-20cd-4838-82b0-5309987a62f0).

The data was retrieved using a Global Fishing Watch (GFW)  API. To get tiled PNGs of fishing effort for each year (from 2012 to 2020), eight `GET` requests were sent to teh GFW API. The request filters data for the desired `date-range` and `geartype`. For the Trawling Activity dataset, we requested data for `dredge_fishing` and `trawlers`. The request returns a url to a tiled png for the filtered fishing activity. Resource Watch draws data directly from this url. <br> 

#### Example: Request for trawling activity from 2012-2013
```
https://gateway.api.globalfishingwatch.org/v1/4wings/generate-png?interval=10days&datasets[0]=public-global-fishing-effort:latest&color=%23ff3f34&date-range=2012-01-01T00:00:00.000Z,2013-01-01T00:00:00.000Z&filters[0]=geartype in ('dredge_fishing','trawlers')
```
##### Note: The request must contain the authorization header and a token as value. Otherwise the request will return an authorization error. GFW has provided WRI Ocean Watch with a token for our use.


<br>You can view the processed Trawling Activity dataset [on Resource Watch](https://resourcewatch.org/data/explore/6ccfb266-20cd-4838-82b0-5309987a62f0).

You can also download the original dataset [from the source website](https://globalfishingwatch.org/data-download/datasets/public-fishing-effort).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Weiqi Zhou](https://www.wri.org/profile/Weiqi-Zhou).
