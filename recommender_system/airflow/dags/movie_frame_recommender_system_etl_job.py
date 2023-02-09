import asyncio
from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import NODES, CLICKHOUSE_CONFIG, MONGO_CONFIG
from src.extract.analytics.clickhouse import ClickhouseExtractor
from src.extract.metadata.admin_api import AdminAPIExtractor
from src.extract.metadata.csv import CSVExtractor
from src.transform.analytics.movie_frame import MovieFrameTransformer as AnalyticsTransformer
from src.transform.metadata.movie_frame import MovieFrameTransformer as MetadataTransformer
from src.transform.recommendation import RecommendationTransformer
from src.load.mongo import AsyncMongoLoader
from modules.als_top.als_src.recommender import start_prepare_data

# Initialize spark session
spark = SparkSession \
    .builder \
    .master('spark://spark-master:7077') \
    .appName("etl_clickhouse_to_spark") \
    .getOrCreate()

spark_context = spark.sparkContext

# ETL clickhouse to spark dataframe
logger.info('[*] Starting etl process clickhouse to spark')

analytics_extractor = ClickhouseExtractor(
    host=NODES[0].HOST,
    port=NODES[0].PORT,
    user=CLICKHOUSE_CONFIG.USER,
    password=CLICKHOUSE_CONFIG.PASSWORD,
    settings={'use_numpy': True}
)
analytics_transformer = AnalyticsTransformer()

analytics_raw_data = analytics_extractor.extract(query="with t as (select user_id, movie_id, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) as metric from t")
analytics_data = analytics_transformer.transform(analytics_raw_data, to_dict=True)

analytics_rdd = spark_context.parallelize(analytics_data)
analytics_dataframe = spark.read.json(analytics_rdd)
logger.info(analytics_dataframe.show(10, False))
logger.info(analytics_dataframe.count())

logger.info('[+] Success finished etl process clickhouse to spark')

# ETL admin api to spark dataframe
logger.info('[*] Starting etl process admin api to spark')

metadata_extractor = CSVExtractor(file_path='/opt/metadata/movies.csv', headers=['id'], with_headers=True)
metadata_transformer = MetadataTransformer()

metadata_raw_data = metadata_extractor.extract()
metadata_data = metadata_transformer.transform(metadata_raw_data, to_dict=True)

metadata_rdd = spark_context.parallelize(metadata_data)
metadata_dataframe = spark.read.json(metadata_rdd)
logger.info(metadata_dataframe.count())
logger.info(metadata_dataframe.show(10, False))

logger.info('[+] Success finished etl process clickhouse to spark')

# Transform analytics data with metadata
logger.info('[*] Transform analytics data with metadata')

dataframe = (analytics_dataframe
    .join(metadata_dataframe, analytics_dataframe.movie_id == metadata_dataframe.id)
    .select(
        analytics_dataframe.user_id, analytics_dataframe.movie_id,
        (analytics_dataframe.metric / metadata_dataframe.duration).alias('metric')
    )
)
dataframe.createOrReplaceGlobalTempView('movie_frame_analytics')

logger.info(dataframe.count())
logger.info(dataframe.show(10, False))

logger.info('[+] Success transforming analytics data with metadata')

# ALS 
logger.info('[*] Starting analyzing with ALS')

#TODO: ALS
result_data = start_prepare_data(
    spark,
    dataframe,
    save_mode=True,
    path_to_csv_file='/opt/metadata/als_top_result_real.csv'
)
logger.info(result_data.count())
logger.info(result_data.show(10, False))

logger.info('[+] Success analyzing with ALS')

# Load to mongodb
logger.info('[*] Loading recommendations to mongo')

# result_transformer = RecommendationTransformer()
# loader = AsyncMongoLoader(settings=MONGO_CONFIG)

#TODO: fake
# import uuid
# result_data = result_transformer.transform([{'user_id': uuid.uuid4(), 'movies_id': [uuid.uuid4(),uuid.uuid4(),uuid.uuid4()]}], to_dict=True)
#
# result = asyncio.run(loader.load(
#     db_name=MONGO_CONFIG.DB_NAME,
#     collection_name=MONGO_CONFIG.COLLECTION_NAME,
#     data=result_data
# ))
# logger.info(result)

logger.info('[+] Success loading recomendations to mongo')
