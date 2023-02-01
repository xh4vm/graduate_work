import logging

from pydantic import BaseSettings


class GRPCSettings(BaseSettings):
    GRPC_HOST: str
    GRPC_PORT: int

    class Config:
        env_prefix = 'RECOMMENDER_'


CONFIG = GRPCSettings()

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
)
grpc_logger = logging.getLogger(name='GRPC Server')
