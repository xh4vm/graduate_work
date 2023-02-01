from abc import ABC, abstractmethod
from dataclasses import dataclass

import backoff
import redis

from config.base import BACKOFF_CONFIG
from config.logger import logger


class BaseStorage(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass


@dataclass
class RedisStorage(BaseStorage):
    redis_client: redis.Redis | redis.StrictRedis

    def get(self, key):
        return self.redis_client.get(key)

    def set(self, key, value):
        return self.redis_client.set(key, value)


@dataclass(frozen=["run_data_key"])
class RunDateStorage:
    storage: BaseStorage
    run_data_key: str = "run_date"

    @backoff.on_exception(**BACKOFF_CONFIG, raise_on_giveup=False)
    def get_run_date(self):
        run_date = self.storage.get(self.run_data_key)
        if isinstance(run_date, bytes):
            run_date = run_date.decode("utf-8")
        return run_date

    @backoff.on_exception(**BACKOFF_CONFIG, raise_on_giveup=False)
    def set_run_date(self, run_date):
        self.storage.set(self.run_data_key, str(run_date))
