from typing import Any

import backoff
from pydantic import BaseSettings, Field


class AirflowDagMovieFrameSettings(BaseSettings):
    SCHEDULE: str

    class Config:
        env_prefix = 'AIRFLOW_DAG_MOVIE_FRAME_'


class SparkSettings(BaseSettings):
    DRIVER: str
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'SPARK_MASTER_'


class HDFSSettings(BaseSettings):
    DRIVER: str
    HOST: str
    PORT: int
    PATH: str

    class Config:
        env_prefix = 'HDFS_'


class DBSettings(BaseSettings):
    DRIVER: str
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'RECOMMENDER_DB_'


class MongoDBSettings(DBSettings):
    DB_NAME: str
    COLLECTION_NAME: str


class AdminApiFakeSettings(BaseSettings):
    DATA_PATH: str

    class Config:
        env_prefix = 'ADMIN_API_FAKE_'


class ClickhouseSettings(BaseSettings):
    NODES: str
    USER: str = Field('default')
    PASSWORD: str = Field('')

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
        if field_name.upper() == 'NODES':
            return [x for x in raw_val.split(',')]
        return cls.json_loads(raw_val)

    class Config:
        env_prefix = 'CH_'


class ClickhouseNode1(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_1')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_1')


class ClickhouseNode2(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_2')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_2')


class ClickhouseNode3(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_3')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_3')


class ClickhouseNode4(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_4')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_4')


NODES = [ClickhouseNode1(), ClickhouseNode2(), ClickhouseNode3(), ClickhouseNode4()]
CLICKHOUSE_CONFIG: ClickhouseSettings = ClickhouseSettings()
MONGO_CONFIG: MongoDBSettings = MongoDBSettings()
HDFS_CONFIG: HDFSSettings = HDFSSettings()
SPARK_CONFIG: SparkSettings = SparkSettings()
ADMIN_API_FAKE_CONFIG: AdminApiFakeSettings = AdminApiFakeSettings()

AIRFLOW_DAG_MOVIE_FRAME_CONFIG: AirflowDagMovieFrameSettings = AirflowDagMovieFrameSettings()

BACKOFF_CONFIG = {'wait_gen': backoff.expo, 'exception': Exception, 'max_value': 8}
