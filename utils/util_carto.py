import os
from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import boto3
from botocore.exceptions import NoCredentialsError
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_to_carto(file):
    '''
    Upload tables to Carto
    INPUT   file: location of file on local computer that you want to upload (string)
    '''
    # set up carto authentication using local variables for username (CARTO_WRI_RW_USER) and API key (CARTO_WRI_RW_KEY)
    auth_client = APIKeyAuthClient(api_key=os.getenv('CARTO_WRI_RW_KEY'), base_url="https://{user}.carto.com/".format(user=os.getenv('CARTO_WRI_RW_USER')))
    # set up dataset manager with authentication
    dataset_manager = DatasetManager(auth_client)
    # upload dataset to carto
    dataset = dataset_manager.create(file)
    logger.info('Carto table created: {}'.format(os.path.basename(file).split('.')[0]))
    # set dataset privacy to 'Public with link'
    dataset.privacy = 'LINK'
    logger.info('Privacy set to public with link.')
    dataset.save()
    
def upload_to_aws(local_file, bucket, s3_file):
    '''
    Upload data to Amazon S3 storage
    INPUT   local_file: local file to be uploaded to AWS (string)
            bucket: AWS bucket where file should be uploaded (string)
            s3_file: path where file should be uploaded within the input AWS bucket (string)
    '''
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('aws_access_key_id'),
                      aws_secret_access_key=os.getenv('aws_secret_access_key'))
    try:
        s3.upload_file(local_file, bucket, s3_file)
        logger.info("AWS upload successful: http://{}.s3.amazonaws.com/{}".format(bucket, s3_file))
        return True
    except FileNotFoundError:
        logger.error("aws_upload - file was not found: + local_file.")
        return False
    except NoCredentialsError:
        logger.error("aws_upload - credentials not available.")
        return False