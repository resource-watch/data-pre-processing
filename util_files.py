import os
import dotenv
dotenv.load_dotenv(os.getenv('RW_ENV'))

def prep_dirs(dataset_name):
    '''
    Sets working directory for processing dataset, and creates needed directories as necessary
    INPUT   dataset_name: full name of dataset to be processed
    RETURN  data_dir: relative path of directory for holding downloaded and processed data
    '''
    # first, set the directory that you are working in with the path variable
    path = os.path.join(os.getenv('PROCESSING_DIR'),dataset_name)
    if not os.path.exists(path):
        os.mkdir(path)
    #move to this directory
    os.chdir(path)

    # create a new sub-directory within your specified dir called 'data'
    # within this directory, create files to store raw and processed data
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    return data_dir

