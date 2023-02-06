import os
from pyspark.sql import DataFrame
import json

from src.db.source.base import SourceDataSet


class FileDataSet(SourceDataSet):
    dataset_folder_path = None

    def __init__(self, spark, folder_path):
        self.spark = spark

    def get_data(self, *args, **kwargs) -> DataFrame:
        return self.spark.read.load(kwargs['filepath'], format='csv', header=True, inferSchema=True)

