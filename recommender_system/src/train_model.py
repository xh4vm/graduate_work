import gc

from src.core.config import SETTINGS
from src.db.source.file_data_source import FileDataSet
from loguru import logger
from tqdm import tqdm
import itertools
from pyspark import SparkContext, SparkConf
from pyspark.mllib.recommendation import ALS
from src.metrics import get_rmse

conf = SparkConf().setAppName("Recommendation service - ALS model evaluation").setMaster(SETTINGS.spark.master)
sc = SparkContext(conf=conf)

datas = FileDataSet(sc, SETTINGS.base_dir)

full_ratings_data = datas.get_data(filename=SETTINGS.file_rating_path)

ratings_data = full_ratings_data.sample(
    withReplacement=False,
    fraction=SETTINGS.sample_size / full_ratings_data.count(),
    seed=SETTINGS.seed
)

# Split data into train, validation datasets
rdd_training, rdd_validating = ratings_data.randomSplit([6, 4], seed=1001)
rdd_validating_no_ratings = rdd_validating.map(lambda x: (int(x[0]), int(x[1])))
rdd_validating_with_ratings = rdd_validating.map(lambda x: ((int(x[0]), int(x[1])), float(x[2])))

nb_validating = rdd_validating.count()

logger.info('Training: {0}, validation: {1}'.format(rdd_training.count(), nb_validating))

final_model = None
final_rank = 0
final_regular = float(0)
final_iter = -1
final_dist = float(300)
final_alpha = float(0)


# START train_model

for c_rank, c_regular, c_iter, c_alpha in tqdm(itertools.product(
    SETTINGS.als.ranks, SETTINGS.als.regular, SETTINGS.als.iters, SETTINGS.als.alpha
)):
    model = ALS.trainImplicit(rdd_training, c_rank, c_iter, float(c_regular), alpha=float(c_alpha))
    predictions = model.predictAll(rdd_validating_no_ratings).map(lambda p: ( (p[0],p[1]), p[2]))
    dist = get_rmse(rdd_validating_with_ratings, nb_validating, predictions)
    if dist < final_dist:
        logger.info('c_iter: {0} c_rank: {1} c_alpha: {2} c_regular: {3}'.format(c_iter, c_rank, c_alpha, c_regular))
        logger.info('Best so far:{0}'.format(dist))
        final_rank = c_rank
        final_regular = c_regular
        final_iter = c_iter
        final_dist = dist
        final_alpha = c_alpha
    del model
    gc.collect()


# final_rank = 5
# final_regular = 0.1
# final_iter = 20
# final_dist = 2.426742063099514
# final_alpha = 40

logger.info('Rank {0}'.format(final_rank))
logger.info('Regular {0}'.format(final_regular))
logger.info('Iter {0}'.format(final_iter))
logger.info('Dist {0}'.format(final_dist))
logger.info('Alpha {0}'.format(final_alpha))

datas.write_best_parameters(
    {'rank': final_rank, 'regul': final_regular, 'iter': final_iter, 'alpha': final_alpha},
    filename=SETTINGS.als.model_params_file_name,
)


if __name__ == '__main__':
    pass




