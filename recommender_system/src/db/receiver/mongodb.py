from pyspark.sql import DataFrame, SparkSession

from src.db.receiver.base import ReceiverDataSet


class MongoDBReceiverDataSet(ReceiverDataSet):

    def __init__(self):
        self.mode = 'overwrite'
        self.format = "com.mongodb.spark.sql.DefaultSource"

    def save_data(self, df: DataFrame, *args, **kwargs):

        # recommendations = DataFrame.map(lambda x: (x[0], [rating.product for rating in x[1]]))
        #
        # recommendations_df = (
        #     self.spark.createDataFrame(recommendations)
        #     .withColumnRenamed('_1', 'user_id')
        #     .withColumnRenamed('_2', 'movies_is')
        # )
        df.write.mode(self.mode).format(self.format).save()
