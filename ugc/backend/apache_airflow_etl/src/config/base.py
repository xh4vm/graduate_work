from pydantic import BaseSettings


class ETLSettings(BaseSettings):
    CH_CLICKHOUSE_NODE_1: str = ""
    CH_CLICKHOUSE_PORT_1: int = 9000
    CH_INIT_DATA_PATH: str
    REDIS_HOST: str = ""
    REDIS_PORT: int = 0
    MOVIES_ADMINPANEL_API_URL: str = ""
    ETL_MOVIE_METADATA_SCHEDULE: str | None = None


ETL_CONFIG: ETLSettings = ETLSettings()
