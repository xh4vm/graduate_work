from abc import ABC, abstractmethod
from pyspark import SparkContext
from pyspark.rdd import RDD


class DataSet(ABC):
    context: SparkContext = None

    @abstractmethod
    def get_data(self, *args, **kwargs) -> RDD:
        pass
