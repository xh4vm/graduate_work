from pathlib import Path

from pydantic import BaseSettings, BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent.parent


class SparkSettings(BaseSettings):
    master: str
    master_host: str
    master_port: int
    app_name: str
    trim_train_dataset: bool = True

    class Config:
        env_prefix = 'SPARK_'
        env_file = Path(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'


class MongoSettings(BaseSettings):
    connect_string: str
    databases: dict
    collection: str
    create_collections_commands_json_file: str
    create_collections_indexes_commands_json_file: str

    class Config:
        env_prefix = 'MONGO_'
        env_file = Path(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'


class AlsSettings(BaseSettings):
    model_params_file_name: str = 'best_model_params.json'
    ranks = [5, 10, 15, 20]
    regular = [0.1, 1, 10]
    iters = [5, 10, 20]
    alpha = [10, 20, 40]
    params: dict = None

    class Config:
        env_prefix = 'ALS_'
        env_file = Path(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    """Class main settings."""
    root_dir = ROOT_DIR
    base_dir = BASE_DIR
    spark = SparkSettings().parse_obj(SparkSettings().dict())
    mongo = MongoSettings().parse_obj(MongoSettings().dict())
    als = AlsSettings().parse_obj(AlsSettings().dict())
    sample_size = 100000
    seed = 1001
    backoff_max_tries = 3
    file_rating_path = 'jupyter-notebook/work/ratings.csv'

    class Config:
        env_prefix = 'PROJECT_'
        env_file = Path(ROOT_DIR, '.env')
