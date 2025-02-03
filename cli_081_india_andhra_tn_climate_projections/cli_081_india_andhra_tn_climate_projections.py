import ee
import os
import sys
from google.cloud import storage
from google_drive_downloader import GoogleDriveDownloader as gdd
import logging
from zipfile import ZipFile
from pathlib import Path

utils_path = os.path.join(os.path.abspath(os.getenv("PROCESSING_DIR")), "utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)
import util_files
import util_cloud

# Get the top-level logger object
logger = logging.getLogger()
for handler in logger.handlers:
    logger.removeHandler(handler)
logger.setLevel(logging.DEBUG)
# make it print to the console.
console = logging.StreamHandler()
logger.addHandler(console)
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# name of asset on GEE where you want to upload data
# this should be an asset name that is not currently in use
dataset_name = "cli_081_india_andhra_tn_climate_projections"
logger.info("Executing script for dataset: " + dataset_name)

data_dir = util_files.prep_dirs(dataset_name)
logger.debug("Data directory relative path: " + data_dir)
logger.debug("Data directory absolute path: " + os.path.abspath(data_dir))

dataset = "climate_data_proj_india_ap_tn_ted"

# Extract the datafiles from the zip
with ZipFile(os.path.join(f"{os.path.abspath(data_dir)}", f"{dataset}.zip"), "r") as zf:
    zf.extractall(os.path.abspath(data_dir))

"""
Process data and upload processed data to Google Earth Engine
"""

# initialize ee and eeUtil modules for uploading to Google Earth Engine

auth = ee.ServiceAccountCredentials(
    os.getenv("GEE_SERVICE_ACCOUT"), os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
ee.Initialize(auth)

# set up Google Cloud Storage project and bucket objects
gcs_client = storage.Client(os.environ.get("CLOUDSDK_CORE_PROJECT"))
gcs_bucket = gcs_client.bucket(os.environ.get("GEE_STAGING_BUCKET"))

indicators = {
    "total_rainfall": "TotalRainfall/Annual",
    "extreme_rainy_days": "ExtremeRainyDays",
    "mean_temp": "MeanTemp",
    "max_temp": "MaxTemp/Annual",
    "min_temp": "MinTemp/Annual",
}
print("creating folder")
 ee.data.createAsset(
    {"type": "Folder"}, "projects/resource-watch-gee/climate_data_proj_india_ap_tn_ted"
 )
print("created folder")
measures = ["mean"]
for indicator, indicator_dir in indicators.items():
    for measure in measures:
        # print(f"projects/resource-watch-gee/{dataset}/{dataset}_{indicator}_{measure}")
        # print(f"{os.path.abspath(data_dir)}/{dataset}/{indicator_dir}")

        image_collection = (
            f"projects/resource-watch-gee/{dataset}/{dataset}_{indicator}_{measure}"
        )
        print(image_collection)
        # create IC
        # Already created by Chris so skip creating the image collection
        ee.data.createAsset({"type": "ImageCollection"}, image_collection)
        # set dataset privacy to public
        acl = {"all_users_can_read": True}
        ee.data.setAssetAcl(image_collection, acl)
        logger.info("Privacy set to public.")

        for path in Path(
            f"{os.path.abspath(data_dir)}/{dataset}/{indicator_dir}"
        ).rglob(f"*_{measure}*"):
            logger.debug(f"Processing {path}")

            image_name = os.path.splitext(os.path.basename(path))[0]

            """
            Upload processed data to Google Earth Engine
            """
            logger.info("Uploading processed data to Google Cloud Storage.")

            # upload local files to Google Cloud Storage
            gs_uris = util_cloud.gcs_upload(
                str(path), os.path.join(dataset, f"{indicator}_{measure}")
            )

            logger.info("Uploading processed data to Google Earth Engine.")

            # set pyramiding policy for GEE upload
            pyramiding_policy = "MEAN"  # check

            # create manifests for upload to GEE
            band_manifest = [
                {
                    "id": "Band1",
                    "tileset_band_index": 0,
                    "tileset_id": os.path.basename(gs_uris[0]).split(".")[0],
                    "pyramidingPolicy": pyramiding_policy,
                }
            ]

            asset_name = f"{image_collection}/{image_name}"
            manifest = util_cloud.gee_manifest_complete(
                asset_name, gs_uris[0], band_manifest
            )

            properties = {
                "SCP": "ssp245.ssp585",
                "change_vs_absolute": "abs",
            }
            manifest["properties"] = properties
            # upload from GCS to GEE
            util_cloud.gee_ingest(manifest, public=True)
            # delete files from GCS
            util_cloud.gcs_remove(gs_uris, gcs_bucket=gcs_bucket)

            logger.info("Files deleted from Google Cloud Storage.")
