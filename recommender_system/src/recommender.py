import pyspark.sql.functions as F
from pydantic import BaseModel
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql.functions import col, row_number
from src.core.config import SETTINGS
from src.core.settings import AlsHeadersCol, AlsParameters, ClickhouseSettings
from src.db.receiver.mongodb import MongoDBReceiverDataSet
from src.db.source.clickhouse import ClickHouseSourceDataSet
# from src.db.source.file_data_source import FileDataSet
from src.engine.spark import SparkManager
from src.predicter.als_predicter import AlsPredictor
from src.utilities.indexer import Indexer


class Recommender:
    class AlsProperties(BaseModel):

        parameters: AlsParameters
        headers_col: AlsHeadersCol
        trim_train_dataset: bool
        sample_size: int
        seed: int

    spark: SparkSession
    data_df: DataFrame
    indexer: Indexer
    als_predictor: AlsPredictor
    als_proper: AlsProperties
    number_top: int
    items_for_user: DataFrame
    prediction_movies_col: str

    def __init__(
        self,
        spark,
        als_proper: AlsProperties,
        number_top: int,
        prediction_movies_col,
        clickhouse_properties: ClickhouseSettings = None,
        file_source_path: str = None
    ):
        self.spark = spark
        self.data_df = ClickHouseSourceDataSet(session=spark, properties=clickhouse_properties).get_data()
        # self.data_df = FileDataSet(spark).get_data(filename=file_source_path)
        self.indexer = Indexer(self.data_df, als_proper.headers_col)
        self.prediction_movies_col = prediction_movies_col

        self.als_predictor = AlsPredictor(
            train_data=self.indexer.string_to_index_als(self.data_df),
            parameters=als_proper.parameters,
            headers_col=als_proper.headers_col,
            number_top=number_top,
            trim_dataset=als_proper.trim_train_dataset,
            sample_size=als_proper.sample_size,
            seed=als_proper.seed,
        )

    def get_top_number_items(self):
        predict_all_raw_id = self.indexer.index_to_string_als(self.als_predictor.top_all)
        window_spec = (
            Window.partitionBy(self.als_proper.headers_col.user_col)
            .orderBy(col(self.als_proper.headers_col.prediction_col).desc()))

        self.items_for_user = (
            predict_all_raw_id.select(
                self.als_proper.headers_col.user_col,
                self.als_proper.headers_col.item_col,
                self.als_proper.headers_col.prediction_col,
                row_number().over(window_spec).alias("rank")
            )
            .where(col("rank") <= self.number_top)
            .groupby(self.als_proper.headers_col.user_col)
            .agg(
                F.collect_list(self.als_proper.headers_col.item_col)
                .alias(self.prediction_movies_col)
            )
        )

    def add_raw_top_movies(self):

        window_spec = Window.orderBy(col('sum({0})'.format(self.als_proper.headers_col.rating_col)).desc())

        raw_top_movies = (
            self.data_df
            .select(
                self.als_proper.headers_col.item_col,
                self.als_proper.headers_col.rating_col,
            )
            .groupby(self.als_proper.headers_col.item_col)
            .sum(self.als_proper.headers_col.rating_col)
            .orderBy(col('sum({0})'.format(self.als_proper.headers_col.rating_col)).desc())
            .select(
                self.als_proper.headers_col.item_col,
                'sum({0})'.format(self.als_proper.headers_col.rating_col),
                row_number().over(window_spec).alias("rank")
            )
            .where(col("rank") <= self.number_top)
            .withColumn(self.als_proper.headers_col.user_col, F.lit('0'))
            .groupby(self.als_proper.headers_col.user_col)
            .agg(
                F.collect_list(self.als_proper.headers_col.item_col)
                .alias(self.prediction_movies_col)
            )
        )

        self.items_for_user = self.items_for_user.union(raw_top_movies)

    def save_recommendations(self, save_mode: str, save_format: str):
        MongoDBReceiverDataSet(save_mode, save_format).save_data(self.items_for_user)


def start_prepare_data():

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s = spark.init_spark(
        app_name=SETTINGS.spark.app_name,
        config_list=[*SETTINGS.clickhouse.config_list, *SETTINGS.mongo.config_list],
    )
    spark_s.sparkContext.setLogLevel('WARN')

    recommender = Recommender(
        spark=spark,
        als_proper=Recommender.AlsProperties(
            parameters=SETTINGS.als.final_parameters,
            headers_col=SETTINGS.als.headers_col,
            trim_train_dataset=SETTINGS.spark.trim_train_dataset,
            sample_size=SETTINGS.sample_size,
            seed=SETTINGS.seed
        ),
        number_top=SETTINGS.number_top,
        clickhouse_properties=SETTINGS.clickhouse,
        prediction_movies_col=SETTINGS.prediction_movies_col,
        )

    recommender.als_predictor.prepare_predictions()

    recommender.get_top_number_items()

    recommender.add_raw_top_movies()

    recommender.save_recommendations(SETTINGS.mongo.save_mode, SETTINGS.mongo.save_format)

    spark_s.stop()


if __name__ == '__main__':

    start_prepare_data()
