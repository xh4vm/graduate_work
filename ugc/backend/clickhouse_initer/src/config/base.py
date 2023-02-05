from typing import Any

import backoff
from pydantic import BaseSettings, Field


class ClickhouseSettings(BaseSettings):
    NODES: str = ""
    USER: str = Field("default")
    PASSWORD: str = Field("")
    INIT_TABLE: str = ""
    INIT_DATA: bool = Field(False)
    INIT_DATA_PATH: str | None
    MOVIE_META_TABLE: str | None

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
        if field_name.upper() == "NODES":
            return [x for x in raw_val.split(",")]
        return cls.json_loads(raw_val)

    class Config:
        env_prefix = "CH_"


class ETLSettings(BaseSettings):
    """Общие настройки для всех ETL процессов, которые касаются загрузки данных в ClickHouse"""

    REDIS_HOST: str = ""
    REDIS_PORT: int = 0
    MOVIES_ADMINPANEL_API_URL: str = ""
    ETL_MOVIE_METADATA_SCHEDULE: str | None = None


CLICKHOUSE_CONFIG: ClickhouseSettings = ClickhouseSettings()
BACKOFF_CONFIG: dict[str, Any] = {
    "wait_gen": backoff.expo,
    "exception": Exception,
    "max_value": 8,
}
ETL_CONFIG: ETLSettings = ETLSettings()
