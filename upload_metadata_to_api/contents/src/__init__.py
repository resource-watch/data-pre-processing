import requests as req
import os
import json
import logging
import sys

import numpy as np
import pandas as pd
logging.basicConfig(stream=sys.stderr, level=logging.INFO)


# Pull in metadata
r = req.get(os.getenv('METADATA_SHEET')).content
current_mdata = pd.read_csv(pd.compat.StringIO(r.decode('utf-8')), header=0)

# Continue with the metadata that matches elements in the tracking sheet
ids_on_backoffice = pd.notnull(current_mdata["RW ID"])
metadata_to_api = current_mdata.loc[ids_on_backoffice]
metadata_to_api = metadata_to_api.reset_index().set_index("RW ID")

# line breaks from html to markdown (b/c newlines not preserved when reading in the google sheet)
metadata_to_api.replace('<br>', '  \n  \n', regex=True, inplace=True)

def clean_nulls(val):
    """Used to clean np.nan values from the metadata update call... which don't play nice with the RW API"""
    try:
        if np.isnan(val):
            return (None)
        else:
            return (val)
    except:
        return (val)


def create_source_object(sources):
    """Format the source information as appropriate for the api"""
    if sources:
        source_object = []
        srcs = sources.split("/")
        for ix, src in enumerate(srcs):
            source_object.append({
                "source-name": src,
                "id": ix,
                "source-description": ""
            })
        return source_object
    return None


def create_headers():
    return {
        'content-type': "application/json",
        'authorization': "{}".format(os.getenv('apiToken')),
    }


def process_description(metadata):
    #first, deal with Archived datasets
    processed_description=''
    if type(metadata['Redirect Dataset ID (archived)'])!=float:
        if metadata['Redirect Dataset ID (archived)']=='X':
            processed_description = processed_description+'_**This dataset has been archived, and we will no longer ' \
                                                          'be updating or maintaining it.**_\n  \n'
        else:
            processed_description = processed_description+'_**This dataset has been archived, and we will no longer ' \
                                                          'be updating or maintaining it. We recommend using [this dataset]' \
                                                          '({}) as a replacement.**_\n  \n'.format(metadata['Redirect Dataset ID (archived)'])
    if type(metadata["Overview"])==str:
        processed_description = processed_description+'### Overview  \n  \n'+metadata["Overview"]
        if type(metadata["Methodology"])==str:
            processed_description = processed_description+'  \n  \n### Methodology  \n  \n'+metadata["Methodology"]
        if type(metadata["Data shown on Resource Watch Map"])==str:
            processed_description = processed_description+'  \n  \n### Data shown on Resource Watch Map  \n  \n'+metadata["Data shown on Resource Watch Map"]
        if type(metadata["Disclaimer"])==str:
            processed_description = processed_description+'  \n  \n### Disclaimer  \n  \n'+ metadata["Disclaimer"]
    else:
        if clean_nulls(metadata["Description"])!=None:
            processed_description = processed_description+clean_nulls(metadata["Description"])
        else:
            processed_description = clean_nulls(metadata["Description"])
    return processed_description


def patch_metadata(info, send=True):
    ds = info[0]
    metadata = info[1]

    rw_api_url = 'https://api.resourcewatch.org/v1/dataset/{}/metadata'.format(ds)
    payload = {"application": "rw", "language": "en"}

    # If the data is of type raster, don't include the Download Data (S3) link
    flag1 = clean_nulls(metadata["Data Type"]) != None
    if (flag1):
        flag2 = clean_nulls(metadata["Data Type"]).lower() != "raster"
        if (flag2):
            data_dl_link = clean_nulls(metadata["Download link"])
        else:
            data_dl_link = None
    else:
        data_dl_link = None

    # If there is no download from source, default to the learn more link
    if (clean_nulls(metadata["Download from Source"]) != None):
        data_dl_orig_link = clean_nulls(metadata["Download from Source"])
    else:
        data_dl_orig_link = clean_nulls(metadata["Learn More Link"])

    # If there is no technical title, default to the public title
    if (clean_nulls(metadata["Formal Name"]) != None):
        tech_title = clean_nulls(metadata["Formal Name"])
    else:
        tech_title = clean_nulls(metadata["Public Title"])

    logging.info("Processing dataset: {}".format(ds))
    row_payload = {
        "language": "en",

        "name": clean_nulls(metadata["Public Title"]),
        "description": process_description(metadata),
        "subtitle": clean_nulls(metadata["Subtitle"]),
        "source": clean_nulls(metadata["Subtitle"]),
        "functions": clean_nulls(metadata["Function"]),

        "application": "rw",
        "dataset": ds,

        "info": {
            "rwId": clean_nulls(metadata["WRI ID"]),

            "data_type": clean_nulls(metadata["Data Type"]),

            "name": clean_nulls(metadata["Public Title"]),
            "sources": create_source_object(clean_nulls(metadata["Source Organizations"])),

            "technical_title": tech_title,

            "functions": clean_nulls(metadata["Function"]),
            "cautions": clean_nulls(metadata["Cautions"]),

            "citation": clean_nulls(metadata["Citation"]),

            "license": clean_nulls(metadata["License"]),
            "license_link": clean_nulls(metadata["License Link"]),

            "geographic_coverage": clean_nulls(metadata["Geographic Coverage"]),
            "spatial_resolution": clean_nulls(metadata["Spatial Resolution"]),

            "date_of_content": clean_nulls(metadata["Date of Content"]),
            "frequency_of_updates": clean_nulls(metadata["Frequency of Updates"]),

            "learn_more_link": clean_nulls(metadata["Learn More Link"]),

            "data_download_link": data_dl_link,
            "data_download_original_link": data_dl_orig_link
        }
    }
    if clean_nulls(metadata["Connector URL"]):
        if 'carto' in clean_nulls(metadata["Connector URL"]):
            row_payload_connector = {
                # "language": "en",
                # "application": "rw",
                "connectorUrl": clean_nulls(metadata["Connector URL"]),
                "tableName": clean_nulls(metadata["Connector URL"].split(os.sep)[-2])
            }
        else:
            row_payload_connector = {
                # "language": "en",
                # "application": "rw",
                "tableName": clean_nulls(metadata["Connector URL"])
            }
    # logging.info(row_payload)
    # logging.info(row_payload_connector)

    if send:
        try:
            res = req.request("POST", rw_api_url, data=json.dumps(row_payload), headers=create_headers())
            if res.ok:
                logging.info('New metadata uploaded')
            else:
                logging.info('Whoops, already exists! Updating metadata.')
                res = req.request("PATCH", rw_api_url, data=json.dumps(row_payload), headers=create_headers())
                logging.info('Ok now?:{}'.format(res.ok))
                if not res.ok:
                    logging.info(res.text)
                    #logging.info(metadata_to_api.loc[ds])
        except TypeError as e:
            logging.info(e.args)
            #logging.info(metadata[["Unique ID", "Public Title"]])
        if clean_nulls(metadata["Connector URL"]):
            try:
                res = req.request("POST", os.path.split(rw_api_url)[0], data=json.dumps(row_payload_connector),
                                  headers=create_headers())
                if res.ok:
                    logging.info('New connector uploaded')
                else:
                    logging.info('Whoops, already exists! Updating connector.')
                    res = req.request("PATCH", os.path.split(rw_api_url)[0], data=json.dumps(row_payload_connector),
                                      headers=create_headers())
                    logging.info('Ok now?:{}'.format(res.ok))
                    if not res.ok:
                        logging.info(res.text)
                        #logging.info(metadata_to_api.loc[ds])
            except TypeError as e:
                logging.info(e.args)
                #logging.info(metadata[["Unique ID", "Public Title"]])
    else:
        with open(row_payload["name"] + ".json", "w") as f:
            f.write(json.dumps(row_payload))


def send_patches(df):
    list(map(patch_metadata, df.iterrows()))


def main():
    send_patches(metadata_to_api)