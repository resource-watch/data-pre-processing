import requests as req
import json
import logging
import numpy as np
import pandas as pd
import sys
import os

logging.basicConfig(stream=sys.stderr, level=logging.INFO)


# Pull in raster interaction metadata
r = req.get(os.getenv('RASTER_INTERACTION_SHEET')).content
current_mdata = pd.read_csv(pd.compat.StringIO(r.decode('utf-8')), header=0, index_col=[0]).iloc[:, 0:10].dropna(subset=["RW Dataset ID", "RW Layer ID", "GEE Asset ID", "Band Name", "Property", "Number Type", "Number of Decimals", "NRT", "Update?"])

# Continue with the metadata that matches elements in the tracking sheet
ids_on_backoffice = pd.notnull(current_mdata["RW Dataset ID"])
metadata_to_api = current_mdata.loc[ids_on_backoffice]
metadata_to_api = metadata_to_api.reset_index().set_index("RW Layer ID")


def get_NRT_int(ds, band, asset, prop, num_type, num_decimals, suffix):
    try:
        num_decimals = int(num_decimals)
        num_format = f'{0:.{num_decimals}f}'
    except:
        if num_decimals == 'scientific':
            num_format = "0,0.0[0]e+0"

    NRT_raster_int = {
        "interactionConfig": {
            "type": "intersection",
            "config": {
                "url": "https://api.resourcewatch.org/v1/query/{ds}?sql=select last({band}) as x from '{asset}'".format(
                    ds=ds, band=band,
                    asset=asset) + " where system:time_start >= 1533448800000 and ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[{{lng}},{{lat}}]}'),4326),the_geom)"
            },
            "pulseConfig": {
                "url": "https://api.resourcewatch.org/v1/query/{ds}?sql=select last({band}) as x from '{asset}'".format(
                    ds=ds, band=band,
                    asset=asset) + " where system:time_start >= 1533448800000 and ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":{{point}}}'),4326),the_geom)"
            },
            "output": [{
                "column": "x",
                "property": "{}".format(prop),
                "type": "{}".format(num_type),
                "format": "{}".format(num_format),
                "suffix": "{}".format(suffix)

            }]}}

    return NRT_raster_int


def get_regular_int(ds, band, asset, prop, num_type, num_decimals, suffix):
    try:
        num_decimals = int(num_decimals)
        num_format = f'{0:.{num_decimals}f}'
    except:
        if num_decimals == 'scientific':
            num_format = "0,0.0[0]e+0"

    regular_raster_int = {
        "interactionConfig": {
            "type": "intersection",
            "config": {
                "url": "https://api.resourcewatch.org/v1/query/{ds}?sql=select st_summarystats(rast, '{band}', false) as x from '{asset}'".format(
                    ds=ds, band=band,
                    asset=asset) + " where ST_INTERSECTS(ST_SetSRID(ST_GeomFromGeoJSON('{\"type\":\"Point\",\"coordinates\":[{{lng}},{{lat}}]}'),4326),the_geom)"
            },
            "output": [{
                "column": "x.{}.mean".format(band),
                "property": "{}".format(prop),
                "type": "{}".format(num_type),
                "format": "{}".format(num_format),
                "suffix": "{}".format(suffix)
            }]}}
    return regular_raster_int


def clean_nulls(val):
    """Used to clean np.nan values from the metadata update call... which don't play nice with the RW API"""
    try:
        if np.isnan(val):
            return (None)
        else:
            return (val)
    except:
        return (val)


def clean_suffixes(val):
    """Used to clean np.nan values from the metadata update call... which don't play nice with the RW API"""
    try:
        if np.isnan(val):
            return (" ")
        else:
            return (" " + val)
    except:
        return (" " + val)


def create_headers():
    return {
        'content-type': "application/json",
        'authorization': "{}".format(os.getenv('apiToken')),
    }


def patch_interactions(info, send=True):
    lyr = info[0]
    metadata = info[1]
    ds = clean_nulls(metadata["RW Dataset ID"])

    rw_api_url = 'https://api.resourcewatch.org/v1/dataset/{dataset_id}/layer/{layer_id}'.format(dataset_id=ds,
                                                                                                 layer_id=lyr)

    payload = {"application": "rw", "language": "en"}

    logging.info("Processing lyr: {}".format(lyr))
    if (clean_nulls(metadata["NRT"]) == "Y"):
        row_payload = get_NRT_int(ds=ds,
                                  band=clean_nulls(metadata["Band Name"]),
                                  asset=clean_nulls(metadata["GEE Asset ID"]),
                                  prop=clean_nulls(metadata["Property"]),
                                  num_type=clean_nulls(metadata["Number Type"]),
                                  num_decimals=clean_nulls(metadata["Number of Decimals"]),
                                  suffix=clean_suffixes(metadata["Suffix"]))

    elif (clean_nulls(metadata["NRT"]) == "N"):
        row_payload = get_regular_int(ds=ds,
                                      band=clean_nulls(metadata["Band Name"]),
                                      asset=clean_nulls(metadata["GEE Asset ID"]),
                                      prop=clean_nulls(metadata["Property"]),
                                      num_type=clean_nulls(metadata["Number Type"]),
                                      num_decimals=clean_nulls(metadata["Number of Decimals"]),
                                      suffix=clean_suffixes(metadata["Suffix"]))
    if send:
        request = []
        error = []
        # logging.info(json.dumps(row_payload))
        try:
            res = req.request("POST", rw_api_url, data=json.dumps(row_payload), headers=create_headers())
            if res.ok:
                logging.info('New metadata uploaded')
            else:
                logging.info('Already exists...updating raster interaction.')
                # logging.info(create_headers())
                res = req.request("PATCH", rw_api_url, data=json.dumps(row_payload), headers=create_headers())
                logging.info('Ok now?:{}'.format(res.ok))
                if not res.ok:
                    request.append(metadata_to_api.loc[lyr])
                    error.append(res.text)
                    # logging.info(metadata_to_api.loc[lyr])
        except TypeError as e:
            logging.info(e.args)
            logging.info(metadata[["RW Layer ID"]])
    return error, request


def send_patches(df):
    errors = []
    requests = []
    for row in df.iterrows():
        error, request = patch_interactions(row)
        if error:
            errors.append(error)
            requests.append(request)
    if len(errors):
        logging.info('Errors sending raster interactions:')
        for i in range(len(errors)):
            logging.info('Request: {}'.format(requests[i]))
            logging.info('Error: {}'.format(errors[i]))


def main():
    send_patches(metadata_to_api)