from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import HDFS_CONFIG, SPARK_CONFIG
from src.schema.movie_frame import OLAP, METADATA


spark = SparkSession \
    .builder \
    .master(f'{SPARK_CONFIG.DRIVER}://{SPARK_CONFIG.HOST}:{SPARK_CONFIG.PORT}') \
    .appName('movie_frame-etl_join_data') \
    .getOrCreate()

analytics_dataframe = spark.read.schema(OLAP).parquet(
    f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-etl-clickhouse-to-parquet'
)
logger.info(analytics_dataframe.show(10, False))

metadata_dataframe = spark.read.schema(METADATA).parquet('hdfs://namenode:9000/parquet/movie-frame-etl-admin-api-to-parquet')

logger.info(metadata_dataframe.show(10, False))

logger.info('[*] Transform analytics data with metadata')

dataframe = (analytics_dataframe
    .join(metadata_dataframe, analytics_dataframe.movie_id == metadata_dataframe.id)
    .select(
        analytics_dataframe.user_id, analytics_dataframe.movie_id,
        (analytics_dataframe.metric / metadata_dataframe.duration).alias('metric')
    )
)

logger.info(dataframe.count())
logger.info(dataframe.show(10, False))

dataframe.write.parquet('hdfs://namenode:9000/parquet/movie-frame-etl-join-data', mode='overwrite')

logger.info('[+] Success transforming analytics data with metadata')
