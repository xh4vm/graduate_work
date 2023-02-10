from pyspark.sql import SparkSession
from loguru import logger

from src.core.config import NODES, CLICKHOUSE_CONFIG, HDFS_CONFIG, SPARK_CONFIG
from src.extract.analytics.clickhouse import ClickhouseExtractor
from src.transform.analytics.movie_frame import MovieFrameTransformer as AnalyticsTransformer
from src.schema.movie_frame import OLAP


spark = SparkSession \
    .builder \
    .master(f'{SPARK_CONFIG.DRIVER}://{SPARK_CONFIG.HOST}:{SPARK_CONFIG.PORT}') \
    .appName('movie_frame-etl_clickhouse_to_parquet') \
    .getOrCreate()

spark_context = spark.sparkContext

logger.info('[*] Starting etl process clickhouse to spark')

extractor = ClickhouseExtractor(
    host=NODES[0].HOST,
    port=NODES[0].PORT,
    user=CLICKHOUSE_CONFIG.USER,
    password=CLICKHOUSE_CONFIG.PASSWORD,
    alt_hosts=[f'{NODE.HOST}:{NODE.PORT}' for NODE in  NODES[1:]],
    settings={'use_numpy': True}
)
transformer = AnalyticsTransformer()

analytics_raw_data = extractor.extract(query="with t as (select user_id, movie_id, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) as metric from t")
analytics_data = transformer.transform(analytics_raw_data, to_dict=True)

rdd = spark_context.parallelize(analytics_data)
dataframe = spark.createDataFrame(rdd, OLAP)

logger.info(dataframe.show(10, False))
logger.info(dataframe.count())
logger.info(dataframe.printSchema())

dataframe.write.parquet(
    path=f'{HDFS_CONFIG.DRIVER}://{HDFS_CONFIG.HOST}:{HDFS_CONFIG.PORT}/{HDFS_CONFIG.PATH}/movie-frame-etl-clickhouse-to-parquet',
    mode='overwrite'
)

logger.info('[+] Success finished etl process clickhouse to spark')
