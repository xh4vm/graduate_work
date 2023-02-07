import gc
import itertools

from loguru import logger
from pydantic import BaseModel
from pyspark import SparkConf, SparkContext
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import DataFrame, SparkSession
from src.core.config import SETTINGS
from src.core.settings import AlsHeadersCol, AlsSettings
# from src.db.source.clickhouse import ClickHouseSourceDataSet
from src.db.source.file_data_source import FileDataSet
from src.utilities.file_utilities import write_best_parameters
from tqdm import tqdm


class AlsTuner:

    class AlsTunerParamsData(BaseModel):
        scores_dataframe: DataFrame
        trim_dataset: bool
        sample_size: int = None
        nb_validating: int = None
        valid_data: DataFrame = None
        train_data: DataFrame = None
        seed: int

        class Config:
            arbitrary_types_allowed = True

    class AlsTunerParamsAls(BaseModel):
        rank: tuple
        iter: tuple
        regular: tuple
        alpha: tuple
        final_parameters: dict = None
        model_params_file_path: str
        headers_col: AlsHeadersCol

    spark: SparkSession
    data_params: AlsTunerParamsData
    als_params: AlsTunerParamsAls
    model: ALS = None

    def __init__(
        self,
        spark_session: SparkSession,
        income_data: DataFrame,
        seed: int,
        als_params: AlsSettings,
        trim_dataset: bool = False,
        sample_size: int = None,
        **kwargs
    ):

        self.spark = spark_session
        self.data_params = self.AlsTunerParamsData(
            scores_dataframe=income_data,
            trim_dataset=trim_dataset,
            sample_size=sample_size,
            seed=seed
        )

        self.model = ALS(
            userCol=self.als_params.headers_col.user_col,
            itemCol=self.als_params.headers_col.item_col,
            ratingCol=self.als_params.headers_col.rating_col,
            coldStartStrategy="drop",
        )

        self.als_params = self.AlsTunerParamsAls(**als_params.dict())

        self.spark.sparkContext.setLogLevel('WARN')

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

        self.als_params.parameters = {
            'rank': final_rank,
            'regular': final_regular,
            'iter': final_iter,
            'alpha': final_alpha,
            'dist': final_dist,
        }

    def tune_als(self):

        if self.data_params.trim_dataset:
            self.data_params.scores_dataframe = self.data_params.scores_dataframe.sample(
                withReplacement=False,
                fraction=self.data_params.sample_size / self.data_params.scores_dataframe.count(),
                seed=self.data_params.seed
            )

        self.data_params.train_data, self.data_params.valid_data = \
            self.data_params.scores_dataframe.randomSplit([6, 4], seed=self.data_params.seed)

        logger.info('Training: {0}, validation: {1}'.format(
            self.data_params.train_data.count(),
            self.data_params.valid_data.count()),
        )

        self.find_parameters()

        logger.info('Best parameters {0}'.format(self.als_params.final_parameters))

        write_best_parameters(**self.als_params.final_parameters, file_path=self.als_params.model_params_file_path)


if __name__ == '__main__':

    conf = SparkConf().setAppName('{0} - Recommender'.format(SETTINGS.spark.app_name)).setMaster(SETTINGS.spark.master)
    sc = SparkContext(conf=conf)

    spark = (
        SparkSession
        .builder
        .appName('{0} - Recommender'.format(SETTINGS.spark.app_name))
        .master(SETTINGS.spark.master)
        .getOrCreate()
             )

    # data_rdd = ClickHouseSourceDataSet(session=spark, properties=SETTINGS.clickhouse).get_data()

    data_rdd = FileDataSet(spark).get_data(filepath=SETTINGS.file_rating_path)

    tuner = AlsTuner(
        spark_context=sc,
        income_data=data_rdd,
        trim_dataset=SETTINGS.spark.trim_train_dataset,
        als_params=SETTINGS.als,
        sample_size=SETTINGS.sample_size,
        seed=SETTINGS.seed,
    )

    tuner.tune_als()

    sc.stop()
