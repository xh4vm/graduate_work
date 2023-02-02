from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class SparkManager:
    master: str

    def __init__(self, master):

        self.master = master

    def init_spark(self, app_name, config_list) -> SparkSession:
        spark_b = SparkSession.builder.master(self.master).appName(app_name)
        for config_unit in config_list:
            spark_b = spark_b.config(*config_unit)

        return spark_b.getOrCreate()
