from typing import Any

import backoff
from pydantic import BaseSettings, Field


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
BACKOFF_CONFIG = {'wait_gen': backoff.expo, 'exception': Exception, 'max_value': 128}
