from pyspark.sql import SparkSession
from random import randint, random
from src.engine.spark import SparkManager
from src.core.config import SETTINGS
from loguru import logger
from src.db.source.clickhouse import ClickHouseDataSet
from pyspark import SparkContext, SparkConf


def generate_date():
    data = []
    count = randint(1, 3)
    for unit in range(count):
        data.append((str(randint(1, 9999)), str(randint(1, 9999)), random()))
    return data


def mongodb_test():
    mongo_connect_string = 'mongodb://mongos1:27017,mongos2:27017'
    mongo_database = 'recommender'
    mongo_collection = 'recommendations'

    app_name = 'test_mongo_connector'
    spark = SparkSession \
        .builder \
        .appName(app_name) \
        .master('spark://spark-master:7077') \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
        .config('spark.mongodb.output.uri', mongo_connect_string)\
        .config('spark.mongodb.output.database', mongo_database)\
        .config('spark.mongodb.output.collection', mongo_collection)\
        .getOrCreate()

    # columns = ['user_id', 'film_id', 'score']
    # data = generate_date()
    #
    # df = spark.createDataFrame(data).toDF(*columns)

    df = spark.createDataFrame(generate_date()).toDF('user_id', 'film_id', 'score')

    df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").save()
    # spark.sparkContext.
    spark.sparkContext.getOrCreate()
    spark.stop()

    # conf = SparkConf().setAppName('TEST').setMaster(
    #     'spark://{0}:{1}'.format('spark-master', '7077')
    # ).set('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2')
    # sc = SparkContext(conf=conf)



def mongodb_with_clickhouse_test():

    mongo_connect_string = 'mongodb://mongos1:27017,mongos2:27017'
    mongo_database = 'recommender'
    mongo_collection = 'recommendations'

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s_in = spark.init_spark(
        app_name='{0} - Input'.format(SETTINGS.spark.app_name),
        config_list=SETTINGS.clickhouse.config_list,
    )
    spark_s_in.sparkContext.setLogLevel('WARN')

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE !!!!!!!!!!!!!!!!!!!')

    data_rdd = ClickHouseDataSet(session=spark_s_in, properties=SETTINGS.clickhouse).get_data()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE COUNT: {0} !!!!!!!!!!!!!!!!!!!'.format(data_rdd.count()))

    # spark_s_in.sparkContext.stop()
    # spark_s_in.stop()
    # del spark_s_in

    # spark_s_out = spark.init_new_spark(
    #     spark_s_in,
    #     app_name='{0} - Output'.format(SETTINGS.spark.app_name),
    #     config_list=SETTINGS.mongo.config_list,
    # )
    # spark_s_out.sparkContext.setLogLevel('WARN')

    spark_s_out = spark_s_in.newSession().builder.appName('{0} - Output'.format(SETTINGS.spark.app_name)).getOrCreate()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! TO MONGODB !!!!!!!!!!!!!!!!!!!')

    columns = ['user_id', 'film_id', 'score']
    data = generate_date()

    df = spark_s_out.createDataFrame(data).toDF(*columns)

    df.write.mode('overwrite')\
        .option('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
        .option('spark.mongodb.output.uri', mongo_connect_string) \
        .option('spark.mongodb.output.database', mongo_database) \
        .option('spark.mongodb.output.collection', mongo_collection) \
        .format("com.mongodb.spark.sql.DefaultSource")\
        .save()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! MONGODB OK !!!!!!!!!!!!!!!!!!!')

    spark_s_out.sparkContext.stop()
    spark_s_out.stop()


def mongodb_with_clickhouse_test1():

    # spark = SparkSession \
    #     .builder \
    #     .appName('TEST') \
    #     .master('spark://spark-master:7077') \
    #     .getOrCreate()
    #
    # spark_c = SparkSession \
    #     .builder \
    #     .appName('TEST CLICK') \
    #     .master('spark://spark-master:7077') \
    #     .config('spark.jars', '/opt/jars/clickhouse-native-jdbc-shaded-2.6.4.jar') \
    #     .getOrCreate()
    #
    # spark_m = SparkSession \
    #     .builder \
    #     .appName('TEST MONGO') \
    #     .master('spark://spark-master:7077') \
    #     .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
    #     .config('spark.mongodb.output.uri', 'mongodb://mongos1:27017,mongos2:27017') \
    #     .config('spark.mongodb.output.database', 'recommender') \
    #     .config('spark.mongodb.output.collection', 'recommendations') \
    #     .getOrCreate()

    spark_all = SparkSession \
        .builder \
        .appName('TEST') \
        .master('spark://spark-master:7077') \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
        .config('spark.jars', '/opt/jars/clickhouse-native-jdbc-shaded-2.6.4.jar') \
        .getOrCreate()

    d = spark_all.read.format("jdbc") \
        .option('driver', 'com.github.housepower.jdbc.ClickHouseDriver') \
        .option('url', 'jdbc:clickhouse://clickhouse-node1:9000') \
        .option('user', 'default') \
        .option('password', '') \
        .option('query', "with t as (select user_id, movie_id, max(movie_duration) as movie_duration, sum(multiIf(event_type == 'starting', -1 * frame_time, event_type == 'stopped', frame_time, 0)) as metric, argMax(frame_time, created_at) as last_frame_time from (SELECT user_id, movie_id, frame_time, movie_duration, event_type, created_at from default.movie_frame ORDER BY created_at) GROUP BY user_id, movie_id) select user_id, movie_id, if(metric <= 0, last_frame_time + metric, metric) / movie_duration as metric from t") \
        .load()

    df = spark_all.createDataFrame(generate_date()).toDF('user_id', 'film_id', 'score')

    df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource") \
        .option('spark.mongodb.output.uri', 'mongodb://mongos1:27017,mongos2:27017') \
        .option('spark.mongodb.output.database', 'recommender') \
        .option('spark.mongodb.output.collection', 'recommendations') \
        .save()


if __name__ == '__main__':

    mongodb_test()
