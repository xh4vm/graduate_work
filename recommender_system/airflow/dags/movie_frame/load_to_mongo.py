import asyncio
from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import MONGO_CONFIG, HDFS_CONFIG, SPARK_CONFIG
from src.transform.recommendation import RecommendationTransformer
from src.load.mongo import AsyncMongoLoader
from src.schema.movie_frame import RECOMMENDATION


spark = SparkSession \
    .builder \
    .master(f'{SPARK_CONFIG.DRIVER}://{SPARK_CONFIG.HOST}:{SPARK_CONFIG.PORT}') \
    .appName('movie_frame-load_to_mongo') \
    .getOrCreate()

dataframe = spark.read.schema(RECOMMENDATION).parquet(
    f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-als'
)

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
