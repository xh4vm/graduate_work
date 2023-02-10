from pyspark.sql import SparkSession
from loguru import logger
from modules.als_top.als_src.recommender import prepare_data

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

predict_top_data = prepare_data(
    spark,
    dataframe,
    demo_mode=True,
    path_from_csv_file='/tmp/metadata/fake_als_top_result.csv',
)
logger.info(predict_top_data.count())
logger.info(predict_top_data.show(10, False))

logger.info('[+] Success analyzing with ALS')

predict_top_data.write.parquet(
    f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-als',
    mode='overwrite'
)
