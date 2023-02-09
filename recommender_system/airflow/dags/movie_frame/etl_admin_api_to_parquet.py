from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType
from loguru import logger

from src.extract.metadata.admin_api import AdminAPIExtractor
from src.extract.metadata.csv import CSVExtractor
from src.transform.metadata.movie_frame import MovieFrameTransformer as MetadataTransformer

schema = StructType(fields=[
    StructField(name='id', dataType=StringType(), nullable=True),
    StructField(name='duration', dataType=LongType(), nullable=True),
])

spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName('movie_frame-etl_admin_api_to_parquet') \
    .getOrCreate()

spark_context = spark.sparkContext

logger.info('[*] Starting etl process admin api to spark')

extractor = CSVExtractor(file_path='/opt/metadata/movies.csv', headers=['id'], with_headers=True)
transformer = MetadataTransformer()

raw_data = extractor.extract()
data = transformer.transform(raw_data, to_dict=True)

rdd = spark_context.parallelize(data)

dataframe = spark.createDataFrame(rdd, schema)

logger.info(dataframe.count())
logger.info(dataframe.show(10, False))
logger.info(dataframe.printSchema())

dataframe.write.parquet(path='/tmp/parquet/movie-frame-etl-admin-api-to-parquet', mode='overwrite')
# dataframe.write \
#     .format("parquet") \
#     .mode("overwrite") \
#     .save("/mnt/parquet/movie-frame-etl-admin-api-to-parquet")

logger.info('[+] Success finished etl process clickhouse to spark')

dataframe2 = spark.read.schema(schema).parquet('/tmp/parquet/movie-frame-etl-admin-api-to-parquet')
# dataframe2 = spark.read.load("/tmp/movie-frame-etl-admin-api-to-parquet", schema=schema, format='parquet')

logger.info(dataframe2.count())
logger.info(dataframe2.show(10, False))
