import json
import os
from os import environ
from dotenv import load_dotenv
from pathlib import Path

from src.utilities.file_utilities import get_data_from_json, get_data_from_file
from src.core.settings import Settings, AlsParameters


def get_settings():
    return Settings()


SETTINGS = get_settings()

if not SETTINGS.spark.master:
    SETTINGS.spark.master = 'spark://{0}:{1}'.format(SETTINGS.spark.master_host, SETTINGS.spark.master_port)

ratings_file = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

if os.path.exists(ratings_file):
    SETTINGS.als.final_parameters = AlsParameters(**get_data_from_json(ratings_file))


SETTINGS.als.model_params_file_path = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

SETTINGS.clickhouse.query = get_data_from_file(
    os.path.join(SETTINGS.base_dir, SETTINGS.clickhouse.query_file_path)
)

SETTINGS.mongo.config_list.extend((
    ('spark.mongodb.output.uri', SETTINGS.mongo.connect_string),
    ('spark.mongodb.output.database', SETTINGS.mongo.databases['db_data']),
    ('spark.mongodb.output.collection', SETTINGS.mongo.collection),
))

pass
