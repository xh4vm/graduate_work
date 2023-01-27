import json
import os
from os import environ
from dotenv import load_dotenv
from pathlib import Path

from src.utilities.file_utilities import get_data_from_json
from src.core.settings import Settings


def get_settings():
    return Settings()


SETTINGS = get_settings()

ratings_file = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

SETTINGS.als.params = get_data_from_json(ratings_file) if os.path.exists(ratings_file) else {
    'rank': 5,
    'regular': 0.1,
    'iter': 5,
    'alpha': 10,
}


pass
