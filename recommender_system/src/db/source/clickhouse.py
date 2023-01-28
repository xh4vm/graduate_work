import os
from pyspark.rdd import RDD
import json

from src.db.source.base import DataSet


class ClickHouseDataSet(DataSet):

    def __init__(self, session, url, properties, query):
        self.session = session
        self.url = url
        self.properties = properties
        self.query = query

    def get_data(self, *args, **kwargs) -> RDD:
        data_frame = self.session.read.format("jdbc") \
            .option('driver', self.properties.get('driver')) \
            .option('url', self.url) \
            .option('user', self.properties.get('user')) \
            .option('password', self.properties.get('password')) \
            .option('query', self.query) \
            .load()

        return data_frame.rdd



