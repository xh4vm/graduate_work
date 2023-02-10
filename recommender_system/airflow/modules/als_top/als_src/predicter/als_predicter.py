from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.sql import DataFrame
from als_src.als_core.settings import AlsHeadersCol, AlsParameters


class AlsPredictor:
    train_data: DataFrame
    items_for_user: DataFrame
    top_all: DataFrame
    parameters: AlsParameters
    headers_col: AlsHeadersCol
    seed: int
    model: ALSModel = None

    def __init__(
        self,
        train_data: DataFrame,
        parameters: AlsParameters,
        headers_col: AlsHeadersCol,
        seed:  int,
    ):
        self.train_data = train_data
        self.parameters = parameters
        self.headers_col = headers_col
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
            .cache()
        )

        del dfs_prediction, dfs_prediction_exclude_train, self.train_data

    def prepare_predictions(self):

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
