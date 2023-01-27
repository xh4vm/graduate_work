from src.core.config import (BASE_DIR, FILE_RATING_PATH, MODEL_PARAMS, SPARK_MASTER_HOST, SPARK_MASTER_PORT,
                             MONGO_CONNECT_STRING, MONGO_DATABASES, MONGO_COLLECTION, SAMPLE_SIZE)
from src.db.source.file_data_source import FileDataSet
from pyspark import SparkContext, SparkConf
from pyspark.mllib.recommendation import ALS
from pyspark.sql import SparkSession
from pyspark.sql.functions import desc


conf = SparkConf().setAppName('Recommendation service - Recommender').setMaster(
    'spark://{0}:{1}'.format(SPARK_MASTER_HOST, SPARK_MASTER_PORT)
)

# conf = SparkConf().setAppName('Recommendation service - Recommender').set(
#     'spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1')

sc = SparkContext(conf=conf)
sc.setLogLevel('WARN')

spark_session = SparkSession.builder.appName(
    'Recommendation service - Recommender'
).config(
    'spark.mongodb.output.uri', MONGO_CONNECT_STRING
).config(
    'spark.mongodb.output.database', MONGO_DATABASES['db_data']
).config(
    'spark.mongodb.output.collection', MONGO_COLLECTION
).getOrCreate()

datas = FileDataSet(sc, BASE_DIR)

full_ratings_data = datas.get_data(filename=FILE_RATING_PATH)
full_data_no_ratings = full_ratings_data.map(lambda x: (int(x[0]), int(x[1])))

sample_size = SAMPLE_SIZE
fraction = sample_size / full_ratings_data.count()

ratings_data = full_ratings_data.sample(False, fraction, 1001)
data_no_ratings = ratings_data.map(lambda x: (int(x[0]), int(x[1])))

model = ALS.trainImplicit(
    ratings_data,
    MODEL_PARAMS['rank'],
    MODEL_PARAMS['iter'],
    float(MODEL_PARAMS['regul']),
    alpha=float(MODEL_PARAMS['alpha'])
)

# rec_users = model.recommendProductsForUsers(30)
predictions = model.predictAll(full_data_no_ratings)
# predictions = model.predictAll(data_no_ratings)

predictions_df = spark_session.createDataFrame(predictions).withColumnRenamed(
    'user', 'user_id'
).withColumnRenamed(
    'product', 'film_id'
).withColumnRenamed('rating', 'score').orderBy('user_id', desc('score'))

predictions_df.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").option(
    'spark.mongodb.output.uri', MONGO_CONNECT_STRING
).option(
    'spark.mongodb.output.database', MONGO_DATABASES['db_data']
).option(
    'spark.mongodb.output.collection', MONGO_COLLECTION
).save()

