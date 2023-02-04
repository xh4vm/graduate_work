from pyspark.sql import SparkSession
from loguru import logger


def clickhouse_test():
# .config('spark.jars', '/opt/jars/clickhouse-native-jdbc-shaded-2.6.4.jar') \

    spark_c = SparkSession \
        .builder \
        .appName('TEST CLICKHOUSE') \
        .master('spark://spark-master:7077') \
        .config('spark.jars', 'com.github.housepower:clickhouse-native-jdbc-shaded:2.6.5') \
        .getOrCreate()

    query = "with t as (select user_id, movie_id, max(movie_duration) as movie_duration, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, movie_duration, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) / movie_duration as metric from t"

    try:
        d = spark_c.read.format("jdbc")\
            .option('driver', 'com.github.housepower.jdbc.ClickHouseDriver')\
            .option('url', 'jdbc:clickhouse://clickhouse-node1:9000')\
            .option('user', 'default')\
            .option('password', '')\
            .option('query', query)\
            .load()
        logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE COUNT: {0} !!!!!!!!!!!!!!!!!!!'.format(d.count()))
    except Exception as err:
        logger.error(err)

    finally:
        spark_c.stop()


if __name__ == '__main__':

    clickhouse_test()
