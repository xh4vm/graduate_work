import os
from os import environ
from dotenv import load_dotenv
from pathlib import Path

from utils.utils import get_data_from_json

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent.parent
load_dotenv(Path(BASE_DIR, '.env'))

SAMPLE_SIZE = 100000
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

FILE_RATING_PATH = 'jupyter-notebook/work/ratings.csv'
