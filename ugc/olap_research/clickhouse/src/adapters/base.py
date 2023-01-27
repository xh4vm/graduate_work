import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import backoff
from clickhouse_driver.errors import NetworkError

from adapters.enums import DBDialects


@dataclass
class BaseDBClient(ABC):
    host: str
    port: str = ""
    connection: Any = None

    @abstractmethod
    def connect(self):
        pass

    @property
    def uri(self):
        port = f":{self.port}" if self.port else ""
        return f"{self.host}{port}"

    @backoff.on_exception(
        backoff.expo, (ConnectionRefusedError, NetworkError), max_tries=10
    )
    def execute(self, text: str):
        if not self.connection:
            self.connect()
        return self.connection.execute(text)


@dataclass
class BaseDBMigrator(ABC):
    client: BaseDBClient
    dialect: str = ""
    db_name: str = ""
    cluster_name: str = ""

    @abstractmethod
    def db_upgrade(self):
        pass


@dataclass
class Model:
    __tablename__: str = ""
    __table_args__: dict = field(default_factory=lambda: {})

    def get_sql_fields(self, dialect: str):
        sql_fields = ""
        model_fields = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        for field_name, field_type in model_fields:
            if isinstance(field_type, TypeGenerator):
                field_value = getattr(self, field_name)
                sql_fields += (
                    f"{field_name} {field_value.sql_representation(dialect)}, "
                )
        return f"({sql_fields[:-2]})"

    def get_sql_args(self, cluster: str = ""):
        keys_to_remove = ("is_distributed",)
        for key in keys_to_remove:
            if key in self.__table_args__:
                del self.__table_args__[key]
        args = ""
        for k, v in self.__table_args__.items():
            args += f"{k} {v} "

        replace_tuple = (("$cluster", cluster), ("$table", self.__tablename__))
        for item in replace_tuple:
            args = args.replace(item[0], item[1])

        return args.strip()

    def is_distributed(self):
        return self.__table_args__.get("is_distributed", False)


@dataclass
class TypeGenerator:
    dict_of_types: dict[str, str]

    def sql_representation(self, dialect: str):
        type_repr = self.dict_of_types.get(dialect, "")
        if not type_repr:
            raise ValueError("SQL type for '%s' dialect is not defined" % dialect)
        return type_repr


class SQLTypes:
    @property
    def int64(self):
        return TypeGenerator({DBDialects.CLICKHOUSE: "Int64"})

    @property
    def float64(self):
        return TypeGenerator({DBDialects.CLICKHOUSE: "Float64"})

    @property
    def date_time(self):
        return TypeGenerator({DBDialects.CLICKHOUSE: "DateTime"})


sql_types = SQLTypes()
