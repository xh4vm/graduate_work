import logging
import backoff
from pydantic import BaseSettings


class GRPCSettings(BaseSettings):
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'RECOMMENDER_GRPC_'


class RedisSettings(BaseSettings):
    HOST: str
    PORT: int
    CACHE_EXPIRE: int
    PASSWORD: str

    class Config:
        env_prefix = 'REDIS_'


class DBSettings(BaseSettings):
    DRIVER: str
    HOST: str
    PORT: int

    class Config:
        env_prefix = 'RECOMMENDER_DB_'


class MongoDBSettings(DBSettings):
    DB_NAME: str
    COLLECTION_NAME: str


class Config(BaseSettings):
    GRPC = GRPCSettings()
    DB = MongoDBSettings()
    CACHE = RedisSettings()

CONFIG = Config()
BACKOFF_CONFIG = {'wait_gen': backoff.expo, 'exception': Exception, 'max_value': 128}

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(name='Recommendation GRPC')
