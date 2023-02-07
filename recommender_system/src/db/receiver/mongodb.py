from pyspark.sql import DataFrame
from src.db.receiver.base import ReceiverDataSet


class MongoDBReceiverDataSet(ReceiverDataSet):

    def __init__(self, mode, sformat):
        self.mode = mode
        self.format = sformat

    def save_data(self, df: DataFrame, *args, **kwargs):
        df.write.mode(self.mode).format(self.format).save()
