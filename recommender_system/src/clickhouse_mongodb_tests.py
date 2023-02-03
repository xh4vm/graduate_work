from pyspark.sql import SparkSession
from loguru import logger
from mongodb_test import generate_date


def mongodb_with_clickhouse_together_test():

    spark_all = SparkSession \
        .builder \
        .appName('TEST') \
        .master('spark://spark-master:7077') \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
        .config('spark.jars', '/opt/jars/clickhouse-native-jdbc-shaded-2.6.4.jar') \
        .getOrCreate()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE !!!!!!!!!!!!!!!!!!!')

    try:
        d = spark_all.read.format("jdbc") \
            .option('driver', 'com.github.housepower.jdbc.ClickHouseDriver') \
            .option('url', 'jdbc:clickhouse://clickhouse-node1:9000') \
            .option('user', 'default') \
            .option('password', '') \
            .option('query', "with t as (select user_id, movie_id, max(movie_duration) as movie_duration, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, movie_duration, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) / movie_duration as metric from t") \
            .load()
        logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE COUNT: {0} !!!!!!!!!!!!!!!!!!!'.format(d.count()))
    except Exception as err:
        logger.error(err)
        spark_all.stop()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! TO MONGODB !!!!!!!!!!!!!!!!!!!')

    df = spark_all.createDataFrame(generate_date()).toDF('user_id', 'film_id', 'score')

    try:
        df.show()
        df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource") \
                .option('spark.mongodb.output.uri', 'mongodb://mongos1:27017,mongos2:27017') \
                .option('spark.mongodb.output.database', 'recommender') \
                .option('spark.mongodb.output.collection', 'recommendations') \
                .save()
    except Exception as err:
        logger.error(err)

    finally:
        spark_all.stop()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! MONGODB OK !!!!!!!!!!!!!!!!!!!')


if __name__ == '__main__':

    mongodb_with_clickhouse_together_test()
