from abc import ABC, abstractmethod
from pyspark.sql import SparkSession


class SparkOutput(ABC):

    @classmethod
    @abstractmethod
    def init_spark(cls, spark_builder: SparkSession.Builder, *args, **kwargs) -> SparkSession.Builder:
        pass


class SparkMongoDB(SparkOutput):

    @classmethod
    @abstractmethod
    def init_spark(cls, spark_builder: SparkSession.Builder, *args, **kwargs) -> SparkSession.Builder:
        spark_builder = spark_builder.config(
            'spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1'
        ).config(
            'spark.mongodb.output.uri', kwargs['connect_string']
        ).config(
            'spark.mongodb.output.database', kwargs['db_name']
        ).config(
            'spark.mongodb.output.collection', kwargs['collection_name']
        )
        return spark_builder


class SparkClickHouse(SparkOutput):

    @classmethod
    @abstractmethod
    def init_spark(cls, spark_builder: SparkSession.Builder, *args, **kwargs) -> SparkSession.Builder:
        spark_builder = spark_builder.config('spark.jars', '/opt/clickhouse-native-jdbc-shaded-2.6.4.jar')
        return spark_builder


spark_manager_receiver = SparkMongoDB()
spark_manager_source = SparkClickHouse()
