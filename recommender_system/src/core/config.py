import json
import os
from os import environ
from dotenv import load_dotenv
from pathlib import Path

from src.utilities.file_utilities import get_data_from_json


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent.parent
load_dotenv(Path(BASE_DIR, '.env'))

SAMPLE_SIZE = 1000
SEED = 1001

# finding best set of parameters
RANKS = [5, 10, 15, 20]
REGULS = [0.1, 1, 10]
ITERS = [5, 10, 20]
ALPHA = [10, 20, 40]

MODEL_PARAMS_FILE_NAME = environ.get('MODEL_PARAMS_FILE_NAME', 'best_model_params.json')

ratings_file = os.path.join(BASE_DIR, MODEL_PARAMS_FILE_NAME)

MODEL_PARAMS = get_data_from_json(ratings_file) if os.path.exists(ratings_file) else {
    'rank': 5,
    'regul': 0.1,
    'iter': 5,
    'alpha': 10,
}

BACKOFF_MAX_TRIES = 3

FILE_RATING_PATH = 'jupyter-notebook/work/ratings.csv'


MONGO_CONNECT_STRING = environ.get('MONGO_CONNECT_STRING')
MONGO_DATABASES = json.loads(environ.get('MONGO_DATABASES', {}))
MONGO_COLLECTION=environ.get('MONGO_COLLECTION')
CREATE_COLLECTIONS_COMMANDS_JSON_FILE = environ.get('CREATE_COLLECTIONS_COMMANDS_JSON_FILE')
CREATE_COLLECTIONS_INDEXES_COMMANDS_JSON_FILE = environ.get('CREATE_COLLECTIONS_INDEXES_COMMANDS_JSON_FILE')

SPARK_MASTER_HOST = environ.get('SPARK_MASTER_HOST')
SPARK_MASTER_PORT = environ.get('SPARK_MASTER_PORT')

pass
