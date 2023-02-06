from pathlib import Path

from pydantic import BaseSettings, BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent


class CommonSettings(BaseSettings):
    class Config:
        env_file = Path(BASE_DIR, '.env')
        env_file_encoding = 'utf-8'


class SparkSettings(CommonSettings):
    master: str = None
    master_host: str
    master_port: int
    app_name: str
    trim_train_dataset: bool = True

    class Config:
        env_prefix = 'SPARK_'


class ClickhouseSettings(CommonSettings):
    url: str
    user: str
    password: str = ''
    driver = 'com.github.housepower.jdbc.ClickHouseDriver'
    query_file_path: str
    query: str = None
    config_list: list = (('spark.jars', '/opt/jars/clickhouse-native-jdbc-shaded-2.6.4.jar'),)

    class Config:
        env_prefix = 'CLICKHOUSE_'


class MongoSettings(CommonSettings):
    connect_string: str
    databases: dict
    collection: str
    create_collections_commands_json_file: str
    create_collections_indexes_commands_json_file: str
    config_list: list = (('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2'),)

    class Config:
        env_prefix = 'MONGO_'


class AlsParameters(BaseModel):
    rank: int = 5
    regular: float = 0.1
    iter: int = 5
    alpha: float = 10.0


class AlsHeadersCol(BaseModel):
    user_col = 'user_id'
    item_col = 'movie_id'
    rating_col = 'metrika'
    prediction_col = "prediction"


class AlsSettings(CommonSettings):
    model_params_file_name: str = 'best_model_params.json'
    model_params_file_path: str = None
    rank = (5, 10, 15, 20)
    regular = (0.1, 1.0, 10.0)
    iter = (5, 10, 20)
    alpha = (10.0, 20.0, 40.0)
    final_parameters: AlsParameters = AlsParameters().parse_obj(AlsParameters().dict())
    headers_col: AlsHeadersCol = AlsHeadersCol().parse_obj(AlsHeadersCol().dict())

    class Config:
        env_prefix = 'ALS_'


class RedisSettings(CommonSettings):
    host: str
    port: int

    class Config:
        env_prefix = 'REDIS_'


REDIS_CONFIG = RedisSettings()


class CelerySettings(BaseModel):
    name = 'recommender_tasks'
    broker = f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}/0'
    backend = f'redis://{REDIS_CONFIG.host}:{REDIS_CONFIG.port}/0'


class Settings(CommonSettings):
    """Class main settings."""
    number_top: int = 30
    root_dir = ROOT_DIR
    base_dir = BASE_DIR
    spark = SparkSettings().parse_obj(SparkSettings().dict())
    clickhouse = ClickhouseSettings().parse_obj(ClickhouseSettings().dict())
    mongo = MongoSettings().parse_obj(MongoSettings().dict())
    als = AlsSettings().parse_obj(AlsSettings().dict())
    celery = CelerySettings().parse_obj(CelerySettings().dict())
    sample_size = 1000
    seed = 1001
    backoff_max_tries = 3
    file_rating_path = 'jupyter-notebook/work/ratings_100.csv'

    class Config:
        env_prefix = 'RECOMMENDER_'

