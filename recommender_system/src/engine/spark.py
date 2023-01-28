from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class SparkManager:
    app_name: str
    master: str

    def __init__(self, app_name, master):

        self.app_name = app_name
        self.master = master

    def init_spark(self, config_list) -> SparkSession:
        spark_b = SparkSession.builder.master(self.master).appName(self.app_name)
        for config_unit in config_list:
            spark_b = spark_b.config(*config_unit)

        return spark_b.getOrCreate()
