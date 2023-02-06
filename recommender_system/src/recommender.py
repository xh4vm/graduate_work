from src.core.settings import AlsHeadersCol, AlsParameters
from src.db.receiver.mongodb import MongoDBReceiverDataSet
from src.db.source.clickhouse import ClickHouseSourceDataSet
from src.engine.spark import SparkManager
from src.core.config import SETTINGS

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark import SparkContext, RDD
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql.functions import col, row_number
import pyspark.sql.functions as F
from src.db.source.file_data_source import FileDataSet


class AlsRecommender:
    spark: SparkSession
    sc: SparkContext
    train_data: DataFrame
    items_for_user: DataFrame
    top_all: DataFrame
    trim_dataset: bool
    sample_size: int = None
    parameters: AlsParameters
    headers_col: AlsHeadersCol
    number_top: int
    seed: int
    model: ALSModel = None

    def __init__(
        self,
        train_data: DataFrame,
        parameters: AlsParameters,
        headers_col: AlsHeadersCol,
        number_top: int,
        seed:  int,
        trim_dataset: bool = False,
        sample_size: int = None,

    ):
        self.train_data = train_data
        self.trim_dataset = trim_dataset
        self.sample_size = sample_size
        self.parameters = parameters
        self.headers_col = headers_col
        self.number_top = number_top
        self.seed = seed

    def create_inference(self):
        users = self.train_data.select(self.headers_col.user_col).distinct()
        items = self.train_data.select(self.headers_col.item_col).distinct()
        user_item = users.crossJoin(items)
        dfs_prediction = self.model.transform(user_item)

        del users, items, user_item

        dfs_prediction_exclude_train = (
            dfs_prediction.alias("prediction")
            .join(
                self.train_data.alias("train"),
                (dfs_prediction[self.headers_col.user_col] == self.train_data[self.headers_col.user_col]) &
                (dfs_prediction[self.headers_col.item_col] == self.train_data[self.headers_col.item_col]),
                how='outer'
            )
        )

        self.top_all = (
            dfs_prediction_exclude_train.filter(
                dfs_prediction_exclude_train[f"train.{self.headers_col.rating_col}"].isNull()
            )
            .select(
                'prediction.' + self.headers_col.user_col,
                'prediction.' + self.headers_col.item_col,
                'prediction.prediction'
            )
        )

        del dfs_prediction, dfs_prediction_exclude_train, self.train_data

    def get_top_number_items(self):

        window_spec = Window.partitionBy(self.headers_col.user_col).orderBy(col(self.headers_col.rating_col).desc())

        self.items_for_user = (
            self.top_all.select(
                self.headers_col.user_col,
                self.headers_col.item_col,
                self.headers_col.rating_col,
                row_number().over(window_spec).alias("rank")
            )
            .where(col("rank") <= self.number_top)
            .groupby(self.headers_col.user_col)
            .agg(F.collect_list(self.headers_col.item_col).alias(self.headers_col.prediction_col))
        )

    def mapping_ids(self):
        pass

    def prepare_recommendations(self):

        if self.trim_dataset:
            sample_size = SETTINGS.sample_size
            fraction = sample_size / self.train_data.count()
            self.train_data = self.train_data.sample(False, fraction, self.seed)

        del self.train_data

        als = ALS(
            rank=self.parameters.rank,
            maxIter=self.parameters.iter,
            implicitPrefs=False,
            regParam=float(self.parameters.regular),
            alpha=float(self.parameters.alpha),
            coldStartStrategy='drop',
            nonnegative=True,
            seed=self.seed,
            userCol=self.headers_col.user_col,
            itemCol=self.headers_col.item_col,
            ratingCol=self.headers_col.rating_col,
            )

        self.model = als.fit(self.train_data)

        self.create_inference()

        self.get_top_number_items()

        self.mapping_ids()


def start_prepare_data():

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s = spark.init_spark(
        app_name=SETTINGS.spark.app_name,
        config_list=[*SETTINGS.clickhouse.config_list, *SETTINGS.mongo.config_list],
    )
    spark_s.sparkContext.setLogLevel('WARN')

    data_df = ClickHouseSourceDataSet(session=spark_s, properties=SETTINGS.clickhouse).get_data()

    # data_df = FileDataSet(spark_s_in.sparkContext, SETTINGS.base_dir).get_data(filename=SETTINGS.file_rating_path)

    recommender = AlsRecommender(
        train_data=data_df,
        parameters=SETTINGS.als.final_parameters,
        headers_col=SETTINGS.als.headers_col,
        number_top=SETTINGS.number_top,
        trim_dataset=SETTINGS.spark.trim_train_dataset,
        sample_size=SETTINGS.sample_size,
        seed=SETTINGS.seed,
    )

    recommender.prepare_recommendations()

    MongoDBReceiverDataSet().save_data(recommender.items_for_user)

    spark_s.stop()


if __name__ == '__main__':

    start_prepare_data()

