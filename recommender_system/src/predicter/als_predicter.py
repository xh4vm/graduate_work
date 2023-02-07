from pyspark import SparkContext
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql import DataFrame, SparkSession
from src.core.config import SETTINGS
from src.core.settings import AlsHeadersCol, AlsParameters

# from src.core.settings import ClickhouseSettings


class AlsPredictor:
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
        users_df = self.train_data.select(self.headers_col.user_col).distinct()
        items_df = self.train_data.select(self.headers_col.item_col).distinct()
        user_item = users_df.crossJoin(items_df)
        dfs_prediction = self.model.transform(user_item)

        del users_df, items_df, user_item

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

    def prepare_predictions(self):

        if self.trim_dataset:
            sample_size = SETTINGS.sample_size
            fraction = sample_size / self.train_data.count()
            self.train_data = self.train_data.sample(False, fraction, self.seed)

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
