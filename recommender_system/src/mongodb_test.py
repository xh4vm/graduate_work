from pyspark.sql import SparkSession
from random import randint, random
from loguru import logger


def generate_date():
    data = []
    count = randint(1, 3)
    for unit in range(count):
        data.append((str(randint(1, 9999)), str(randint(1, 9999)), random()))
    return data


def mongodb_test():

    spark_m = SparkSession \
        .builder \
        .appName('TEST MONGO') \
        .master('spark://spark-master:7077') \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.2') \
        .config('spark.mongodb.output.uri', 'mongodb://mongos1:27017,mongos2:27017') \
        .config('spark.mongodb.output.database', 'recommender') \
        .config('spark.mongodb.output.collection', 'recommendations') \
        .getOrCreate()

    df = spark_m.createDataFrame(generate_date()).toDF('user_id', 'film_id', 'score')

    try:
        df.show()
        df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").save()
        logger.info('!!!!!!!!!!!!!!!!!!!!!!!!!!!! MONGODB OK !!!!!!!!!!!!!!!!!!!')

    except Exception as err:
        logger.error(err)

    finally:
        spark_m.stop()


if __name__ == '__main__':

    mongodb_test()
