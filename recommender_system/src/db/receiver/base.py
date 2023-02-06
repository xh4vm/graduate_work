from abc import ABC, abstractmethod
from pyspark.sql import DataFrame, SparkSession


class ReceiverDataSet(ABC):
    spark: SparkSession = None

    @abstractmethod
    def save_data(self, df: DataFrame, *args, **kwargs):
        pass
