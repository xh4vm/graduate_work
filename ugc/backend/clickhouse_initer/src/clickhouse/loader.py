from dataclasses import dataclass
from typing import Iterator

import backoff
from clickhouse_driver.errors import NetworkError
from pydantic import BaseModel

from clickhouse.client import ClickhouseClient
from config.logger import logger
from loader.base import BaseLoader


@dataclass
class ClickhouseLoader(BaseLoader):
    client: ClickhouseClient

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=NetworkError, max_tries=10, logger=logger
    )
    def insert(self, data: Iterator[BaseModel], **kwargs) -> None:
        table: str = kwargs.get("table", "")
        response = self.client.conn.execute(
            f"INSERT INTO {table} VALUES", (_.dict() for _ in data)
        )
        return response
