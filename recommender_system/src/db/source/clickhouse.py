from pyspark.sql import DataFrame, SparkSession
from src.core.settings import ClickhouseSettings
from src.db.source.base import SourceDataSet


class ClickHouseSourceDataSet(SourceDataSet):

    def __init__(self, session: SparkSession, properties: ClickhouseSettings):
        self.session = session
        self.properties = properties

    def get_data(self, *args, **kwargs) -> DataFrame:
        data_frame = self.session.read.format("jdbc") \
            .option('driver', self.properties.driver) \
            .option('url', self.properties.url) \
            .option('user', self.properties.user) \
            .option('password', self.properties.password) \
            .option('query', self.properties.query) \
            .load()
        return data_frame
