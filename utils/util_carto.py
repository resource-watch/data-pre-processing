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
    
