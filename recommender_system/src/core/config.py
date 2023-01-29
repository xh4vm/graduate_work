import json
import os
from os import environ
from dotenv import load_dotenv
from pathlib import Path

from src.utilities.file_utilities import get_data_from_json, get_data_from_file
from src.core.settings import Settings


def get_settings():
    return Settings()


SETTINGS = get_settings()

if not SETTINGS.spark.master:
    SETTINGS.spark.master = 'spark://{0}:{1}'.format(SETTINGS.spark.master_host, SETTINGS.spark.master_port)

ratings_file = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

SETTINGS.als.final_parameters = get_data_from_json(ratings_file) if os.path.exists(ratings_file) else {
    'rank': 5,
    'regular': 0.1,
    'iter': 5,
    'alpha': 10,
}

SETTINGS.als.model_params_file_path = os.path.join(SETTINGS.base_dir, SETTINGS.als.model_params_file_name)

SETTINGS.clickhouse.query = get_data_from_file(
    os.path.join(SETTINGS.base_dir, SETTINGS.clickhouse.query_file_path)
)

SETTINGS.spark.config_list = (
    # ('spark.jars', '/opt/clickhouse-native-jdbc-shaded-2.6.4.jar, '
    #                '/opt/org.mongodb.spark:mongo-spark-connector_2.12:3.0.1.jar'),
    ('spark.mongodb.write.connection.uri', SETTINGS.mongo.connect_string),
    # ('spark.mongodb.output.uri', SETTINGS.mongo.connect_string),
    ('spark.mongodb.write.database', SETTINGS.mongo.databases['db_data']),
    # ('spark.mongodb.output.database', SETTINGS.mongo.databases['db_data']),
    ('spark.mongodb.write.collection', SETTINGS.mongo.collection),
    # ('spark.mongodb.output.collection', SETTINGS.mongo.collection),
)



pass
