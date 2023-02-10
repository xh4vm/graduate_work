from pyspark.ml.feature import StringIndexer
from pyspark.sql import DataFrame
from pyspark.sql.functions import col
from als_src.als_core.settings import AlsHeadersCol


class Indexer:
    users: DataFrame
    items: DataFrame
    headers_col: AlsHeadersCol

    def __init__(self, data: DataFrame, headers: AlsHeadersCol):
        self.headers_col = headers
        users_original = data.select(self.headers_col.user_col).distinct()
        items_original = data.select(self.headers_col.item_col).distinct()
        self.users = self._indexing(users_original, self.headers_col.user_col)
        self.items = self._indexing(items_original, self.headers_col.item_col)
        del users_original, items_original

    @classmethod
    def _indexing(cls, data: DataFrame, column_name: str) -> DataFrame:
        column_int = '{0}_int'.format(column_name)
        string_indexer = StringIndexer(inputCol=column_name, outputCol=column_int)
        model = string_indexer.fit(data)
        return model.transform(data).withColumn(column_int, col(column_int).cast("integer"))

    def string_to_index_als(self, data_to_als: DataFrame) -> DataFrame:
        user_int_col = '{0}_int'.format(self.headers_col.user_col)
        item_int_col = '{0}_int'.format(self.headers_col.item_col)
        return (
            data_to_als
            .join(self.users, [self.headers_col.user_col])
            .join(self.items, [self.headers_col.item_col])
            .drop(self.headers_col.user_col, self.headers_col.item_col)
            .select(user_int_col, item_int_col, self.headers_col.rating_col)
            .withColumnRenamed(user_int_col, self.headers_col.user_col)
            .withColumnRenamed(item_int_col, self.headers_col.item_col)
        )

    def index_to_string_als(self, data_from_als: DataFrame) -> DataFrame:
        user_int_col = '{0}_int'.format(self.headers_col.user_col)
        item_int_col = '{0}_int'.format(self.headers_col.item_col)
        return (
            data_from_als
            .withColumnRenamed(self.headers_col.user_col, user_int_col)
            .withColumnRenamed(self.headers_col.item_col, item_int_col)
            .join(self.users, [user_int_col])
            .join(self.items, [item_int_col])
            .drop(item_int_col, user_int_col)
        )
