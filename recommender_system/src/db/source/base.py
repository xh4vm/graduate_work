from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession


class SourceDataSet(ABC):
    spark: SparkSession = None

    @abstractmethod
    def get_data(self, *args, **kwargs) -> DataFrame:
        pass