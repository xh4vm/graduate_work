from abc import ABC, abstractmethod


class AsyncDBStorage(ABC):

    @abstractmethod
    async def exec_command(self, db_name: str, command: dict, *args, **kwargs):
        pass

    @abstractmethod
    async def drop_collections(self):
        pass
