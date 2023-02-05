from src.db.source.clickhouse import ClickHouseDataSet
from src.engine.spark import SparkManager
from src.core.config import SETTINGS

from pyspark.sql import SparkSession
from pyspark import SparkContext, RDD
from pyspark.mllib.recommendation import ALS
from pyspark.sql.functions import desc, collect_list

from src.db.source.file_data_source import FileDataSet


class AlsRecommender:
    spark: SparkSession
    sc: SparkContext
    scores_dataframe: RDD
    trim_dataset: bool
    sample_size: int = None
    rank: int = 5
    iter: int = 5
    regular: float = 0.1
    alpha: float = 10.0

    def __init__(
        self,
        spark_session: SparkSession,
        scores_dataframe: RDD,
        rank: int,
        _iter: int,
        regular: float,
        alpha: float,
        trim_dataset: bool = False,
        sample_size: int = None,
    ):
        self.spark = spark_session
        self.sc = spark_session.sparkContext
        self.scores_dataframe = scores_dataframe
        self.trim_dataset = trim_dataset
        self.sample_size = sample_size
        self.rank = rank
        self.iter = _iter
        self.regular = regular
        self.alpha = alpha

    def save_recommendations(self, predictions: RDD):

        predictions_df = self.spark.createDataFrame(predictions).withColumnRenamed(
            'user', 'user_id'
        ).orderBy('user_id', desc('rating'))

        group_by_user = predictions_df.groupBy('user_id').agg(collect_list('product')).alias('movies_id')

        group_by_user.write.mode('overwrite').format("com.mongodb.spark.sql.DefaultSource").save()

    def prepare_recommendations(self):

        if self.trim_dataset:
            sample_size = SETTINGS.sample_size
            fraction = sample_size / self.scores_dataframe.count()
            scores_data = self.scores_dataframe.sample(False, fraction, 1001)
        else:
            scores_data = self.scores_dataframe

        del self.scores_dataframe

        data_no_scores = scores_data.map(lambda x: (int(x[0]), int(x[1])))

        model = ALS.trainImplicit(
            scores_data,
            self.rank,
            self.iter,
            float(self.regular),
            alpha=float(self.alpha)
        )

        predictions = model.predictAll(data_no_scores)

        del model, data_no_scores

        self.save_recommendations(predictions)


def start_prepare_data():

    spark = SparkManager(master=SETTINGS.spark.master)

    spark_s_in = spark.init_spark(
        app_name='{0} - Input'.format(SETTINGS.spark.app_name),
        config_list=SETTINGS.clickhouse.config_list,
    )
    spark_s_in.sparkContext.setLogLevel('WARN')

    spark_s_out = spark.init_spark(
        app_name='{0} - Output'.format(SETTINGS.spark.app_name),
        config_list=SETTINGS.mongo.config_list,
    )
    spark_s_out.sparkContext.setLogLevel('WARN')

    # data_rdd = ClickHouseDataSet(session=spark_s_in, properties=SETTINGS.clickhouse).get_data()

    data_rdd = FileDataSet(spark_s_in.sparkContext, SETTINGS.base_dir).get_data(filename=SETTINGS.file_rating_path)

    spark_s_in.stop()

    recommender = AlsRecommender(
        spark_s_out,
        data_rdd,
        rank=SETTINGS.als.final_parameters['rank'],
        _iter=SETTINGS.als.final_parameters['iter'],
        regular=float(SETTINGS.als.final_parameters['regular']),
        alpha=float(SETTINGS.als.final_parameters['alpha']),
        trim_dataset=SETTINGS.spark.trim_train_dataset,
        sample_size=SETTINGS.sample_size,
    )

    recommender.prepare_recommendations()

    spark_s_out.stop()


if __name__ == '__main__':

    start_prepare_data()

