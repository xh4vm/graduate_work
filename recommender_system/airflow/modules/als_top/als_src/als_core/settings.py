from pathlib import Path

from pydantic import BaseModel, BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent.parent.parent.parent


class CommonSettings(BaseSettings):
    class Config:
        env_file = Path(ROOT_DIR, '.env')
        env_file_encoding = 'utf-8'


class SparkSettings(CommonSettings):
    master: str = None
    master_host: str
    master_port: int
    config_list: list = (('spark.driver.extraJavaOptions', '-Xss16m'), ('spark.executor.extraJavaOptions', '-Xss16m'))

    class Config:
        env_prefix = 'SPARK_'


class AlsParameters(BaseModel):
    rank: int = 5
    regular: float = 0.1
    iter: int = 5
    alpha: float = 10.0
    dist: float = 0.0


class AlsHeadersCol(BaseModel):
    user_col = 'user_id'
    item_col = 'movie_id'
    rating_col = 'metric'
    prediction_col = "prediction"


class AlsSettings(CommonSettings):
    model_params_file_name: str
    model_params_file_path: str = None
    rank = (5, 10, 15, 20)
    regular = (0.1, 1.0, 10.0)
    iter = (5, 10, 20)
    alpha = (10.0, 20.0, 40.0)
    final_parameters: AlsParameters = AlsParameters().parse_obj(AlsParameters().dict())
    headers_col: AlsHeadersCol = AlsHeadersCol().parse_obj(AlsHeadersCol().dict())

    class Config:
        env_prefix = 'ALS_'


class Settings(CommonSettings):
    """Class main settings."""
    number_top: int
    root_dir = ROOT_DIR
    base_dir = BASE_DIR
    spark = SparkSettings().parse_obj(SparkSettings().dict())
    als = AlsSettings().parse_obj(AlsSettings().dict())
    seed = 1001
    prediction_movies_col = "movies_id"
    path_to_csv: str = '/tmp/metadata/als_top_result.csv'

    class Config:
        env_prefix = 'RECOMMENDER_ALS_'
