from services.storage.base import BaseDB


class AsyncMongoDB(BaseDB):
    @property
    def conn(self):
        pass

    def get(self):
        pass
