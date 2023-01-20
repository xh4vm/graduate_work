import inspect
import time
from dataclasses import dataclass
from typing import Type

from clickhouse_driver import Client
from loguru import logger

from adapters import models
from adapters.base import Model, BaseDBClient, BaseDBMigrator
from adapters.enums import DBDialects

MODELS_MODULE_NAME = models.__name__


@dataclass
class ClickHouseClient(BaseDBClient):
    def connect(self):
        self.connection = Client(host=self.host, port=self.port)


@dataclass
class ClickHouseMigrator(BaseDBMigrator):
    dialect: str = DBDialects.CLICKHOUSE
    db_name: str = ""
    cluster_name: str = ""

    def db_exists(self):
        for item in self.client.execute("SHOW DATABASES") or []:
            if len(item) > 0 and item[0] == self.db_name:
                return True
        return False

    def db_healthy(self, timeout: int = 15):
        logger.info(
            "Waiting for db '%s' on host '%s'" % (self.db_name, self.client.uri)
        )
        n = 0
        while not self.db_exists() and n < timeout:
            time.sleep(1)
            n += 1
        return n < timeout or self.db_exists()

    def db_upgrade(self):
        if self.db_healthy():
            logger.info(
                "DB '%s' is available on host '%s'" % (self.db_name, self.client.uri)
            )
            tables = self._get_tables()
            for table in tables:
                self.create_table(self._get_db_for_table(table), table)
        else:
            logger.error(
                "Database '%s' is unavailable on '%s'" % (self.db_name, self.client.uri)
            )

    def create_table(self, db: str, table: Type[Model]):
        table_instance = table()
        query = (
            """CREATE TABLE IF NOT EXISTS {db}.{table} {fields} {extra_args};""".format(
                db=db,
                table=table.__tablename__,
                fields=table_instance.get_sql_fields(self.dialect),
                extra_args=table_instance.get_sql_args(self.cluster_name),
            )
        )
        self.client.execute(query)

    @classmethod
    def _is_table(cls, member):
        return (
            inspect.isclass(member)
            and member.__module__ == MODELS_MODULE_NAME
            and Model in inspect.getmro(member)
        )

    def _get_tables(self):
        tables = [item[1] for item in inspect.getmembers(models, self._is_table)]
        return sorted(tables, key=lambda x: x().is_distributed())

    def _get_db_for_table(self, model):
        return "default" if model().is_distributed() else self.db_name
