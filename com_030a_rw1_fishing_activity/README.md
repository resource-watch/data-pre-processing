## Fishing Activity Dataset Pre-processing
This file describes the data pre-processing that was done to [Global Fishing Activity](https://globalfishingwatch.org/?utm_source=wri_map&utm_medium=api_integration&utm_campaign=ocean_watch) for [display on Resource Watch](https://resourcewatch.org/data/explore/11f16cb9-def0-4bd5-a60e-50c542b837e3).

The data was retrieved using a Global Fishing Watch (GFW)  API. To get tiled PNGs of fishing effort for each year (from 2012 to 2020), eight `GET` requests were sent to teh GFW API. The request filters data for the desired `date-range` and `geartype`. For the Fishing Activity dataset, we requested all gear types except `dredge_fishing` and `trawlers`. The request returns a url to a tiled png for the filtered fishing activity. Resource Watch draws data directly from this url.<br>

#### Example: Request for fishing activity from 2012-2013
```
https://gateway.api.globalfishingwatch.org/v1/4wings/generate-png?interval=10days&datasets[0]=public-global-fishing-effort:latest&color=%23f20089&date-range=2012-01-01T00:00:00.000Z,2013-01-01T00:00:00.000Z&filters[0]=geartype in ('tuna_purse_seines','driftnets','trollers','set_longlines','purse_seines','pots_and_traps','other_fishing','set_gillnets','fixed_gear','fishing','seiners','other_purse_seines','other_seines','squid_jigger','pole_and_line','drifting_longlines')
```

##### Note: The request must contain the authorization header and a token as value. Otherwise the request will return an authorization error. GFW has provided WRI Ocean Watch with a token for our use.


<br>You can view the processed Fishing Activity dataset [on Resource Watch](https://resourcewatch.org/data/explore/11f16cb9-def0-4bd5-a60e-50c542b837e3).

You can also download the original dataset [from the source website](https://globalfishingwatch.org/data-download/datasets/public-fishing-effort).

###### Note: This dataset processing was done by [Rachel Thoms](https://www.wri.org/profile/rachel-thoms), and QC'd by [Weiqi Zhou](https://www.wri.org/profile/Weiqi-Zhou).
