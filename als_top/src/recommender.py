import pyspark.sql.functions as F
from pydantic import BaseModel
from pyspark import RDD
from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import col, row_number
from src.core.config import SETTINGS
from src.core.settings import AlsHeadersCol, AlsParameters
from src.engine.spark import SparkManager
from src.predicter.als_predicter import AlsPredictor
from src.utilities.indexer import Indexer


class Recommender:
    class AlsProperties(BaseModel):

        parameters: AlsParameters
        headers_col: AlsHeadersCol
        seed: int

    data_df: DataFrame
    indexer: Indexer
    als_predictor: AlsPredictor
    als_proper: AlsProperties
    number_top: int
    items_for_user: DataFrame
    prediction_movies_col: str

    def __init__(
        self,
        data_df: DataFrame,
        als_proper: AlsProperties,
        number_top: int,
        prediction_movies_col,
    ):
        self.data_df = data_df
        self.indexer = Indexer(self.data_df, als_proper.headers_col)
        self.prediction_movies_col = prediction_movies_col

        self.als_predictor = AlsPredictor(
            train_data=self.indexer.string_to_index_als(self.data_df),
            parameters=als_proper.parameters,
            headers_col=als_proper.headers_col,
            number_top=number_top,
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


def start_prepare_data(data_rdd: RDD):

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s = spark.init_spark(
        app_name=SETTINGS.spark.app_name,
        config_list=SETTINGS.spark.config_list,
    )

    data_df = spark_s.createDataFrame(
        data_rdd,
        list(SETTINGS.als.headers_col.dict(exclude={'prediction_col'}).values())
    )

    recommender = Recommender(
        data_df=data_df,
        als_proper=Recommender.AlsProperties(
            parameters=SETTINGS.als.final_parameters,
            headers_col=SETTINGS.als.headers_col,
            seed=SETTINGS.seed
        ),
        number_top=SETTINGS.number_top,
        prediction_movies_col=SETTINGS.prediction_movies_col,
    )

    recommender.als_predictor.prepare_predictions()

    recommender.get_top_number_items()

    recommender.add_raw_top_movies()

    return recommender.items_for_user
