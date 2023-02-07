from pyspark.sql import DataFrame, SparkSession
from src.db.source.base import SourceDataSet


class FileDataSet(SourceDataSet):
    dataset_folder_path = None

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def get_data(self, *args, **kwargs) -> DataFrame:
        data = self.spark.read.load(kwargs['filepath'], format='csv', header=True, inferSchema=True)
        return (
            data
            .withColumnRenamed('userId', 'user_id')
            .withColumnRenamed('movieId', 'movie_id')
            .withColumnRenamed('rating', 'metric')
            .select('user_id', 'movie_id', 'metric')
        )
