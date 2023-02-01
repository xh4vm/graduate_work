from dataclasses import dataclass
from typing import Iterator

from pydantic import BaseModel

from clickhouse.client import ClickhouseClient
from loader.base import BaseLoader


@dataclass
class ClickhouseLoader(BaseLoader):
    client: ClickhouseClient

    def insert(self, data: Iterator[BaseModel], **kwargs) -> None:
        table: str = kwargs.get("table", "")
        response = self.client.conn.execute(
            f"INSERT INTO {table} VALUES", (_.dict() for _ in data)
        )
        return response
