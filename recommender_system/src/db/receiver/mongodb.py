from pyspark.sql import DataFrame, SparkSession

from src.db.receiver.base import ReceiverDataSet


class MongoDBReceiverDataSet(ReceiverDataSet):

    def __init__(self):
        self.mode = 'overwrite'
        self.format = "com.mongodb.spark.sql.DefaultSource"

    def save_data(self, df: DataFrame, *args, **kwargs):

        recommendations_df = self.spark.createDataFrame(df).withColumnRenamed('prediction', 'movies_is')

        recommendations_df.write.mode(self.mode).format(self.format).save()
