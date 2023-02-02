from pyspark.sql import SparkSession
from random import randint, random
from src.engine.spark import SparkManager
from src.core.config import SETTINGS
from loguru import logger
from src.db.source.clickhouse import ClickHouseDataSet


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

    columns = ['user_id', 'film_id', 'score']
    data = generate_date()

    df = spark.createDataFrame(data).toDF(*columns)

    df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").save()

    spark.stop()


def mongodb_with_clickhouse_test():

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s_in = spark.init_spark(
        app_name='{0} - Input'.format(SETTINGS.spark.app_name),
        config_list=SETTINGS.clickhouse.config_list,
    )
    spark_s_in.sparkContext.setLogLevel('WARN')

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE !!!!!!!!!!!!!!!!!!!')

    data_rdd = ClickHouseDataSet(session=spark_s_in, properties=SETTINGS.clickhouse).get_data()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! FROM CLICKHOUSE COUNT: {0} !!!!!!!!!!!!!!!!!!!'.format(data_rdd.count()))

    spark_s_in.sparkContext.stop()
    spark_s_in.stop()
    del spark_s_in

    spark_s_out = spark.init_spark(
        app_name='{0} - Output'.format(SETTINGS.spark.app_name),
        config_list=SETTINGS.mongo.config_list,
    )
    spark_s_out.sparkContext.setLogLevel('WARN')

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! TO MONGODB !!!!!!!!!!!!!!!!!!!')

    columns = ['user_id', 'film_id', 'score']
    data = generate_date()

    df = spark_s_out.createDataFrame(data).toDF(*columns)

    df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").save()

    logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! MONGODB OK !!!!!!!!!!!!!!!!!!!')

    spark_s_out.sparkContext.stop()
    spark_s_out.stop()


if __name__ == '__main__':

    mongodb_test()
