from pathlib import Path

from pydantic import BaseSettings, BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

pass
class CommonSettings(BaseSettings):
    class Config:
        env_file = Path(ROOT_DIR, '.env')
        env_file_encoding = 'utf-8'


class MongoSettings(CommonSettings):
    connect_string: str
    databases: dict
    collection: str
    create_collections_commands_json_file: str
    create_collections_indexes_commands_json_file: str
    config_list: list = (('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2'),)

    class Config:
        env_prefix = 'MONGO_'


class Settings(BaseModel):
    """Class main settings."""
    root_dir = ROOT_DIR
    base_dir = BASE_DIR
    mongo = MongoSettings().parse_obj(MongoSettings().dict())
    backoff_max_tries = 3


SETTINGS = Settings()

pass

