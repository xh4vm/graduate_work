from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from loguru import logger


spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName('movie_frame-als') \
    .getOrCreate()

schema = StructType(fields=[
    StructField(name='metric', dataType=FloatType(), nullable=False),
    StructField(name='movie_id', dataType=StringType(), nullable=False),
    StructField(name='user_id', dataType=StringType(), nullable=False),
])

dataframe = spark.read.schema(schema).parquet('/tmp/movie-frame-etl-join-data')

logger.info('[*] Starting analyzing with ALS')

logger.info(dataframe.show(10, False))

#TODO: ALS 

logger.info('[+] Success analyzing with ALS')

dataframe.write.mode('overwrite').parquet('/tmp/movie-frame-als')
