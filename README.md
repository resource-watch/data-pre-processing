# Resource Watch Dataset Pre-processing Github
#### Purpose
This Github repository was created to document the pre-processing done to any dataset displayed on [Resource Watch](https://resourcewatch.org/).

#### File Structure
The processing done to each dataset should be stored in a single file, named with the WRI ID and public title used on Resource Watch. This folder should **always** include a README.md file that describes the processing that was done. A template for this file can be found in this repository with the name README_template.md. If a script (preferably Python) was used to process the dataset, that code should also be included as a separate file. The general structure can be summarized as follows:

```
Repository
|
|- Dataset 1 folder = {wri_id}_{public_title}
| |-{wri_id}_{public_title}_processing.py # optional, script used to process the dataset
| |-README.md # file describing the processing
| +-...
|
|-Dataset 2 folder
| +-...
|
+-...
```

#### Contents of README.md
If the pre-processing was done in Excel, and functions used should be clearly described. If it was done in Carto, any SQL statements should be included as code snippets. For datasets that were processed in Google Earth Engine (GEE), a link to the GEE script should be included, AND the code should be included in the README.md file as a code snippet for users who do not have access to Google Earth Engine.

#### Contents of script, if included
If a script was used to process the dataset, the code should be uploaded to this Github. This code should be thoroughly commented so that readers unfamiliar with the coding language can still follow the process.

All codes should be written using open-source tools and programming languages. Tools and modules that require a subscription should be avoided (e.g., ArcGIS).


