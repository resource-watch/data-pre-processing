## {Resource Watch Public Title} Dataset Pre-processing
This file describes the data pre-processing that was done to [IRENA Renewable Energy Capacity](https://irena.org/publications/2020/Mar/Renewable-Capacity-Statistics-2020) and [IRENA Renewable Energy Generation]() to prepare for their upload to Resource Watch.

IRENA annually releases [a publication](https://irena.org/publications/2020/Mar/Renewable-Capacity-Statistics-2020) on capacity and renewable energy generation by nation, year, and technology.
This information is readily accessed through their [Data and Statistics page](https://irena.org/Statistics/View-Data-by-Topic/Capacity-and-Generation/Statistics-Time-Series), and can be downloaded from a Tableau dashboard.
As an example this dataset has granularity for capacity (units of MW) or generation (units of GWh) that looks like `{2015, Cambodia, Onshore Wind, On-grid}`.

This directory holds scripts to produce **two** datasets for upload.

### Data License
The publication [IRENA Renewable Energy Capacity](https://irena.org/publications/2020/Mar/Renewable-Capacity-Statistics-2020) states:

```
Copyright (c) IRENA 2020
Unless otherwise stated, material in this publication may be freely used, shared, copied,
reproduced, printed and/or stored, provided that appropriate acknowledgement is given of
IRENA as the source and copyright holder.
Material in this publication that is attributed to third parties may be subject
to separate terms of use and restrictions, and appropriate permissions from
these third parties may need to be secured before any use of such material.
```

The Tableau download does not clearly denote its license availability.


### Data Acquisition
1. Point web browser to:
   [https://public.tableau.com/views/IRENARETimeSeries/Charts?%3Aembed=y&%3AshowVizHome=no&publish=yes&%3Atoolbar=no](https://public.tableau.com/views/IRENARETimeSeries/Charts?%3Aembed=y&%3AshowVizHome=no&publish=yes&%3Atoolbar=no)

2. Ensure right-side dimensions are set to:
   ```
   "level_of_detail": "cumulative",
   "flow": "Electricity Generation",
   "grid_connection": "(all)",
   "region": "(all)",
   "country/area": "(all)",
   "technology": "(all)",
   "sub-technology": "(all)",
   "year": "(all)"
   ```

3. Click the excel icon in the top-right.
   This file can be discarded - it is not needed.
   This step is necessary to activate the button for step 5.

4. Click the download icon in the bottom right, within the Tableau footer

5. Select 'data' from the format options

6. Switch to the 'Full Data' tab

7. Select the 'Show all columns' checkbox

8. Click "Download all rows as a text file"

9. Copy the downloaded file into this python script's parent directory

10. Name the file the value of `LOCAL_INPUT_FILE` in the script, or the converse


### Data Processing
Please see the [Python scripts]() for more details on this processing.
A quick overview is that the data is aggregated based on year, country, sub-technology (e.g. onshore wind, solar thermal, etc), and on-grid/off-grid.
The initial input file contains both generation and capacity rows, so those are subset early on.

This processing follows the original choice by IRENA to default to filtering out Pumped Storage hydro plants.
These plants are downloaded in the original file to be complete, but are not present in the transformed data.


You can view the processed dataset [on Resource Watch]().

###### Note: This dataset processing was done by [Logan Byers](https://www.wri.org/profile/logan-byers), and QC'd by [{name}]({link to WRI bio page}).
