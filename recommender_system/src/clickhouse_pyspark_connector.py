#!/usr/bin/env python

from pyspark.sql import SparkSession

ABSOLUTE_PATH_TO_JARFILE = '/opt/jars/clickhouse-jdbc-0.3.2.jar'
# CLICKHOUSE_JAR = f'file://{ABSOLUTE_PATH_TO_JARFILE}'


def init_spark(app_name: str):

    spark_session = (
        SparkSession
        .builder
        .appName(app_name)
        .master('spark://spark-master:7077')
        .config('spark.jars', ABSOLUTE_PATH_TO_JARFILE) \
        )

    spark = (
        spark_session
        .getOrCreate()
    )

    return spark


def do_test():
    spark = init_spark("Clickhouse test ")
    query = "with t as (select user_id, movie_id, max(movie_duration) as movie_duration, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, movie_duration, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) / movie_duration as metric from t"

    # database = os.environ.get('CH_DATABASE')
    # dbtable = f'{database}.table'
    url = 'jdbc:clickhouse://clickhouse-node1:9000'
    user = 'default'
    password = ''
    driver = 'ru.yandex.clickhouse.ClickHouseDriver'

    df = (
        spark.read.format('jdbc')
        .option('driver', driver)
        .option('url', url)
        .option('user', user)
        .option('password', password)
        .option('query', query)
        .load()
    )

    print(df.show(5))

    spark.stop()


if __name__ == '__main__':

    do_test()
