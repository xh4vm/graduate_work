from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
from loguru import logger


spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName('movie_frame-etl_join_data') \
    .getOrCreate()

analytics_schema = StructType(fields=[
    StructField(name='metric', dataType=DoubleType(), nullable=True),
    StructField(name='movie_id', dataType=StringType(), nullable=True),
    StructField(name='user_id', dataType=StringType(), nullable=True),
])

analytics_dataframe = spark.read.schema(analytics_schema).parquet('/tmp/movie-frame-etl-clickhouse-to-parquet')
logger.info(analytics_dataframe.show(10, False))

metadata_schema = StructType(fields=[
    StructField(name='duration', dataType=LongType(), nullable=False),
    StructField(name='id', dataType=StringType(), nullable=False),
])

metadata_dataframe = spark.read.schema(metadata_schema).parquet('/tmp/movie-frame-etl-admin-api-to-parquet')

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

dataframe.write.mode('overwrite').parquet('/tmp/movie-frame-etl-join-data')

logger.info('[+] Success transforming analytics data with metadata')
