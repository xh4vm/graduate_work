from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from loguru import logger
from modules.als_top.als_src.recommender import prepare_data


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

predict_top_data = prepare_data(
    spark,
    dataframe,
    demo_mode=True,
    path_from_csv_file='/tmp/metadata/fake_als_top_result.csv',
)
logger.info(predict_top_data.count())
logger.info(predict_top_data.show(10, False))

logger.info('[+] Success analyzing with ALS')

predict_top_data.write.mode('overwrite').parquet('/tmp/movie-frame-als')
