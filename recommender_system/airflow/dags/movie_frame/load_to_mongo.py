import asyncio
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from loguru import logger

from src.core.config import MONGO_CONFIG
from src.transform.recommendation import RecommendationTransformer
from src.load.mongo import AsyncMongoLoader


spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName('movie_frame-load_to_mongo') \
    .getOrCreate()

schema = StructType(fields=[
    StructField(name='movies_id', dataType=ArrayType(elementType=StringType), nullable=False),
    StructField(name='user_id', dataType=StringType(), nullable=False),
])

dataframe = spark.read.schema(schema).parquet('/tmp/movie-frame-als')

logger.info('[*] Loading recomendations to mongo')

result_transformer = RecommendationTransformer()
loader = AsyncMongoLoader(settings=MONGO_CONFIG)

#TODO: fake
import uuid
result_data = result_transformer.transform([{'user_id': uuid.uuid4(), 'movies_id': [uuid.uuid4(),uuid.uuid4(),uuid.uuid4()]}], to_dict=True)

result = asyncio.run(loader.load(
    db_name=MONGO_CONFIG.DB_NAME,
    collection_name=MONGO_CONFIG.COLLECTION_NAME,
    data=result_data
))
logger.info(result)

logger.info('[+] Success loading recomendations to mongo')