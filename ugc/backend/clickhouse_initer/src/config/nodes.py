from pydantic import BaseSettings, Field


class ClickhouseNode1(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_1')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_1')
    SCHEMA_NAME: str = Field(..., env='CLICKHOUSE_SCHEMA_NAME_1')


class ClickhouseNode2(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_2')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_2')
    SCHEMA_NAME: str = Field(..., env='CLICKHOUSE_SCHEMA_NAME_2')


class ClickhouseNode3(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_3')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_3')
    SCHEMA_NAME: str = Field(..., env='CLICKHOUSE_SCHEMA_NAME_3')


class ClickhouseNode4(BaseSettings):
    HOST: str = Field(..., env='CLICKHOUSE_NODE_4')
    PORT: int = Field(..., env='CLICKHOUSE_PORT_4')
    SCHEMA_NAME: str = Field(..., env='CLICKHOUSE_SCHEMA_NAME_4')


NODES = [ClickhouseNode1(), ClickhouseNode2(), ClickhouseNode3(), ClickhouseNode4()]
