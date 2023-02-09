import os

from als_src.als_core.settings import AlsParameters, Settings
from als_src.utilities.file_utilities import get_data_from_json


def get_settings():
    return Settings()


SETTINGS = get_settings()

if not SETTINGS.spark.master:
    SETTINGS.spark.master = 'spark://{0}:{1}'.format(SETTINGS.spark.master_host, SETTINGS.spark.master_port)

ratings_file = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

if os.path.exists(ratings_file):
    SETTINGS.als.final_parameters = AlsParameters(**get_data_from_json(ratings_file))


SETTINGS.als.model_params_file_path = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

pass
