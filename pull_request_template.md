## Checklist for Reviewing a Pre-Processing Script

- [ ] Does the python script contain the following 4 sections: Download data and save to your data directory, Process data, Upload processed data to Carto/Upload processed data to Google Earth Engine, Upload original data and processed data to Amazon S3 storage?
- [ ] Does the script have the standardized variable names for: dataset_name, raw_data_file, processed_data_file?
- [ ] Does the script create and use a 'data' directory?
- [ ] Does the script use a python module to automatically download the data? If this is not possible, are there explicit instructions for how to download the data (step by step with instructions about every input parameter and button to click to find the exact data) and does it use shutil to move the data from 'Downloads' into the data directory?
- [ ] Is the script automated as much as possible to minimize rewriting code the next time the dataset updates (ex 1: can you automatically pull out column names instead of typing them yourself? ex 2: if you are dropping columns with no data, did you use pandas to find the nodata columns instead of dropping the column by name?)
- [ ] Are there comments on almost every line of code to explicitly state what is being done and why?
- [ ] Are you uploading to the correct AWS location?
- [ ] For GEE scripts, did you explicitly define the band manifest with a pyramiding policy so that we can easily change it later if we need to?
- [ ] Does the README contain all relevant links?
- [ ] Does the README state the original file type?
- [ ] Does the README list all of the processing steps that were taken in the script?
- [ ] For netcdfs, does the README state which variables were pulled from the netcdf?
- [ ] Did you use the util functions whenever possible?
- [ ] Have you checked the processed data file on your computer to make sure it matches the data you uploaded to Carto? (spaces or symbol names in column titles often get changed in the upload process-please change these before uploading so that the backed up processed data matches the data on Carto)
- [ ] Does the folder name and python script file name match the dataset_name variable in the script? Are they all lowercase? Does the processing script end in '_processing.py'? (this part is often forgotten)
