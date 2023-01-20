import os
from pathlib import Path
from typing import Any

from pydantic import BaseSettings

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


class OLAPResearchSettings(BaseSettings):
    OLAP_RESEARCH_QUERIES_PATH: str = ""
    OLAP_RESEARCH_LOAD_BENCH_SIZE: int = 1000000

    class Config:
        env_file = os.path.join(ROOT_DIR, ".env")
        env_file_encoding = "utf-8"


class CHSettings(BaseSettings):
    CH_CLUSTER_NAME: str
    CH_DB_NAME: str
    CH_REPLICA_DB_NAME: str
    CH_NODE_NUM: int
    CH_NODE_PREFIX: str
    CH_NODE_PORTS: list[int]
    CH_LOCAL_MODE: bool = True

    class Config:
        env_file = os.path.join(ROOT_DIR, ".env")
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name.upper() == "CH_NODE_PORTS":
                return [int(x) for x in raw_val.split(",")]
            return cls.json_loads(raw_val)


ch_settings = CHSettings()
olap_research_settings = OLAPResearchSettings()
