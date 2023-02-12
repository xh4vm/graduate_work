from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import HDFS_CONFIG, SPARK_CONFIG, ADMIN_API_FAKE_CONFIG
from src.extract.metadata.admin_api import AdminAPIExtractor
from src.extract.metadata.csv import CSVExtractor
from src.transform.metadata.movie_frame import FakeMovieFrameTransformer as MetadataTransformer
from src.schema.movie_frame import METADATA


spark = SparkSession \
    .builder \
    .master(f'{SPARK_CONFIG.DRIVER}://{SPARK_CONFIG.HOST}:{SPARK_CONFIG.PORT}') \
    .appName('movie_frame-etl_admin_api_to_parquet') \
    .getOrCreate()

spark_context = spark.sparkContext

logger.info('[*] Starting etl process admin api to spark')

extractor = CSVExtractor(file_path=ADMIN_API_FAKE_CONFIG.DATA_PATH)
transformer = MetadataTransformer()

raw_data = extractor.extract()
data = transformer.transform(raw_data, to_dict=True)

rdd = spark_context.parallelize(data)

dataframe = spark.createDataFrame(rdd, METADATA)

logger.info(dataframe.count())
logger.info(dataframe.show(10, False))
logger.info(dataframe.printSchema())

dataframe.write.parquet(
    path=f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-etl-admin-api-to-parquet',
    mode='overwrite'
)

logger.info('[+] Success finished etl process clickhouse to spark')
