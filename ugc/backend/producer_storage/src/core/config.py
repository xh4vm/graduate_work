import logging
from logging import config as logging_config

from pydantic import BaseSettings, Field

from .logger import LOGGING


class Settings(BaseSettings):
    class Config:
        env_file = '../../../.env'


class AppSettings(Settings):
    HOST: str = Field('localhost')
    PORT: int
    PROJECT_NAME: str
    API_PATH: str
    API_URL: str
    SCHEMA_REGISTRY_URL: str
    API_VERSION: str
    SWAGGER_PATH: str
    JSON_SWAGGER_PATH: str

    class Config:
        env_prefix = 'PRODUCER_STORAGE_'


class KafkaTopicsSettings(Settings):
    MOVIE_FRAME: str

    class Config:
        env_prefix = 'PRODUCER_STORAGE_KAFKA_TOPICS_'


class KafkaSettings(Settings):
    SERVERS: str
    TOPICS: BaseSettings = Field(default_factory=KafkaTopicsSettings)

    class Config:
        env_prefix = 'PRODUCER_STORAGE_KAFKA_'


class Config(Settings):
    APP: AppSettings = AppSettings()
    KAFKA: KafkaSettings = KafkaSettings()


CONFIG = Config()

logging_config.dictConfig(LOGGING)
service_logger = logging.getLogger('PRODUCER STORAGE SERVICE')
