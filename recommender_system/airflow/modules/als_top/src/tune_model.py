import gc
import itertools

from loguru import logger
from pydantic import BaseModel
from pyspark import RDD
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import DataFrame, SparkSession
from src.core.config import SETTINGS
from src.core.settings import AlsParameters, AlsSettings
from src.engine.spark import SparkManager
from src.utilities.file_utilities import write_best_parameters
from tqdm import tqdm


class AlsTuner:

    class AlsTunerParamsData(BaseModel):
        scores_dataframe: DataFrame
        nb_validating: int = None
        valid_data: DataFrame = None
        train_data: DataFrame = None
        seed: int

        class Config:
            arbitrary_types_allowed = True

    spark: SparkSession
    data_params: AlsTunerParamsData
    als_params: AlsSettings
    model: ALS = None
    new_als_params: AlsParameters = None

    def __init__(
        self,
        income_data: DataFrame,
        seed: int,
        als_params: AlsSettings,
        **kwargs
    ):
        self.als_params = als_params
        self.data_params = self.AlsTunerParamsData(
            scores_dataframe=income_data,
            seed=seed,
        )

        self.model = ALS(
            userCol=self.als_params.headers_col.user_col,
            itemCol=self.als_params.headers_col.item_col,
            ratingCol=self.als_params.headers_col.rating_col,
            coldStartStrategy="drop",
        )

    def find_parameters(self):

        final_rank = 0
        final_regular = float(0)
        final_iter = -1
        final_dist = float(300)
        final_alpha = float(0)

        for c_rank, c_regular, c_iter, c_alpha in tqdm(itertools.product(
            self.als_params.rank, self.als_params.regular, self.als_params.iter, self.als_params.alpha
        )):
            als = self.model.setAlpha().setMaxIter(c_iter).setRank(c_rank).setRegParam(c_regular)

            new_model = als.fit(self.data_params.train_data)

            predictions = new_model.transform(self.data_params.valid_data)

            evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")

            dist = evaluator.evaluate(predictions)

            if dist < final_dist:
                logger.info(
                    'c_iter: {0} c_rank: {1} c_alpha: {2} c_regular: {3}'.format(c_iter, c_rank, c_alpha, c_regular))
                logger.info('Best so far:{0}'.format(dist))
                final_rank = c_rank
                final_regular = c_regular
                final_iter = c_iter
                final_dist = dist
                final_alpha = c_alpha

            del new_model, als, predictions
            gc.collect()

        self.new_als_params = AlsParameters(
            rank=final_rank,
            regular=final_regular,
            iter=final_iter,
            alpha=final_alpha,
            dist=final_dist,
        )

    def tune_als(self):

        self.data_params.train_data, self.data_params.valid_data = \
            self.data_params.scores_dataframe.randomSplit([6, 4], seed=self.data_params.seed)

        logger.info('Training: {0}, validation: {1}'.format(
            self.data_params.train_data.count(),
            self.data_params.valid_data.count()),
        )

        self.find_parameters()

        logger.info('Best parameters {0}'.format(self.als_params.final_parameters))

        write_best_parameters(self.new_als_params.dict(), file_path=self.als_params.model_params_file_path)


def turn_als(data_df: DataFrame):

    tuner = AlsTuner(
        income_data=data_df,
        als_params=SETTINGS.als,
        seed=SETTINGS.seed,
    )

    tuner.tune_als()

    return tuner.new_als_params.dict()
