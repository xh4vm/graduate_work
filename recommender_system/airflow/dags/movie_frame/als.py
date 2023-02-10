from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import HDFS_CONFIG, SPARK_CONFIG
from src.schema.movie_frame import ALS


spark = SparkSession \
    .builder \
    .master(f'{SPARK_CONFIG.DRIVER}://{SPARK_CONFIG.HOST}:{SPARK_CONFIG.PORT}') \
    .appName('movie_frame-als') \
    .getOrCreate()

dataframe = spark.read.schema(ALS).parquet(
    f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-etl-join-data'
)

logger.info('[*] Starting analyzing with ALS')

logger.info(dataframe.show(10, False))

#TODO: ALS 

logger.info('[+] Success analyzing with ALS')

dataframe.write.parquet(
    f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-als',
    mode='overwrite'
)
