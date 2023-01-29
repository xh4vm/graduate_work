import gc
from src.core.config import SETTINGS
from src.core.settings import AlsSettings
from src.db.source.base import DataSet
from src.db.source.file_data_source import FileDataSet
from loguru import logger
from tqdm import tqdm
import itertools
from pyspark import SparkContext, SparkConf, RDD
from pyspark.mllib.recommendation import ALS
from src.metrics import get_rmse
from pydantic import BaseModel

from src.utilities.file_utilities import write_best_parameters


class AlsTuner:

    class AlsTunerParamsData(BaseModel):
        scores_dataframe: RDD
        trim_dataset: bool
        sample_size: int = None
        nb_validating: int = None
        rdd_validating_with_ratings: RDD = None
        rdd_validating_no_ratings: RDD = None
        rdd_training: RDD = None
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

    sc: SparkContext
    data_params: AlsTunerParamsData
    als_params: AlsTunerParamsAls

    def __init__(
        self,
        spark_context: SparkContext,
        income_data: RDD,
        seed: int,
        als_params: AlsSettings,
        trim_dataset: bool = False,
        sample_size: int = None,
        **kwargs
    ):

        self.sc = spark_context
        self.data_params = self.AlsTunerParamsData(
            scores_dataframe=income_data,
            trim_dataset=trim_dataset,
            sample_size=sample_size,
            seed=seed
        )

        self.als_params = self.AlsTunerParamsAls(**als_params.dict())

        self.sc.setLogLevel('WARN')

    def find_parameters(self):
        final_rank = 0
        final_regular = float(0)
        final_iter = -1
        final_dist = float(300)
        final_alpha = float(0)
        for c_rank, c_regular, c_iter, c_alpha in tqdm(itertools.product(
            self.als_params.rank, self.als_params.regular, self.als_params.iter, self.als_params.alpha
        )):

            model = ALS.trainImplicit(
                self.data_params.rdd_training,
                c_rank,
                c_iter,
                float(c_regular),
                alpha=float(c_alpha),
            )

            predictions = model.predictAll(self.data_params.rdd_validating_no_ratings).map(
                lambda p: ((p[0], p[1]), p[2])
            )

            dist = get_rmse(self.data_params.rdd_validating_with_ratings, self.data_params.nb_validating, predictions)
            if dist < final_dist:
                logger.info(
                    'c_iter: {0} c_rank: {1} c_alpha: {2} c_regular: {3}'.format(c_iter, c_rank, c_alpha, c_regular))
                logger.info('Best so far:{0}'.format(dist))
                final_rank = c_rank
                final_regular = c_regular
                final_iter = c_iter
                final_dist = dist
                final_alpha = c_alpha
            del model, predictions
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

        self.data_params.rdd_training, rdd_validating = self.data_params.scores_dataframe.randomSplit([6, 4], seed=1001)
        self.data_params.rdd_validating_no_ratings = rdd_validating.map(lambda x: (int(x[0]), int(x[1])))
        self.data_params.rdd_validating_with_ratings = rdd_validating.map(
            lambda x: ((int(x[0]), int(x[1])), float(x[2]))
        )

        self.data_params.nb_validating = rdd_validating.count()

        logger.info('Training: {0}, validation: {1}'.format(
            self.data_params.rdd_training.count(),
            self.data_params.nb_validating),
        )

        self.find_parameters()

        logger.info('Best parameters {0}'.format(self.als_params.final_parameters))

        write_best_parameters(**self.als_params.final_parameters, file_path=self.als_params.model_params_file_path)


if __name__ == '__main__':

    conf = SparkConf().setAppName('{0} - Recommender'.format(SETTINGS.spark.app_name)).setMaster(SETTINGS.spark.master)
    sc = SparkContext(conf=conf)

    # data_rdd = ClickHouseDataSet(session=spark_s, properties=SETTINGS.clickhouse).get_data()

    data_rdd = FileDataSet(sc, SETTINGS.base_dir).get_data(filename=SETTINGS.file_rating_path)

    tuner = AlsTuner(
        spark_context=sc,
        dataset=data_rdd,
        trim_dataset=SETTINGS.spark.trim_train_dataset,
        als_params=SETTINGS.als,
        sample_size=SETTINGS.sample_size,
        seed=SETTINGS.seed,
    )

    tuner.tune_als()

    sc.stop()




