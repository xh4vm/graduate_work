from core.config import (BASE_DIR, SAMPLE_SIZE, SEED,
                         RANKS, REGULS, ITERS, ALPHA,
                         MODEL_PARAMS_FILE_NAME, FILE_RATING_PATH)
from db.file_data_source import FileDataSet
from loguru import logger
from tqdm import tqdm
import itertools
from pyspark import SparkContext, SparkConf
from pyspark.mllib.recommendation import ALS
from metrics import get_rmse
from utils.utils import quiet_logs

conf = SparkConf().setAppName("Recommendation service - ALS model evaluation")
sc = SparkContext(conf=conf)

quiet_logs(sc)

datas = FileDataSet(sc, BASE_DIR)

full_ratings_data = datas.get_data(filename=FILE_RATING_PATH)

ratings_data = full_ratings_data.sample(
    withReplacement=False,
    fraction=SAMPLE_SIZE / full_ratings_data.count(),
    seed=SEED
)

# Split data into train, validation datasets
rdd_training, rdd_validating = ratings_data.randomSplit([6, 4], seed=1001)
rdd_validating_no_ratings = rdd_validating.map(lambda x: (int(x[0]), int(x[1])))
rdd_validating_with_ratings = rdd_validating.map(lambda x: ((int(x[0]),int(x[1])), float(x[2])))

nb_validating = rdd_validating.count()

logger.info('Training: {0}, validation: {1}'.format(rdd_training.count(), nb_validating))

final_model = None
final_rank = 0
final_regul = float(0)
final_iter = -1
final_dist = float(300)
final_alpha = float(0)


# START train_model

for c_rank, c_regul, c_iter, c_alpha in tqdm(itertools.product(RANKS, REGULS, ITERS, ALPHA)):
    model = ALS.trainImplicit(rdd_training, c_rank, c_iter, float(c_regul),alpha=float(c_alpha))
    predictions = model.predictAll(rdd_validating_no_ratings).map(lambda p: ( (p[0],p[1]), p[2]))
    dist = get_rmse(rdd_validating_with_ratings, nb_validating, predictions)
    if dist < final_dist:
        logger.info('c_iter: {0} c_rank: {1} c_alpha: {2} c_regul: {3}'.format(c_iter, c_rank, c_alpha, c_regul))
        logger.info('Best so far:{0}'.format(dist))
        final_rank = c_rank
        final_regul = c_regul
        final_iter = c_iter
        final_dist = dist
        final_alpha = c_alpha
    del model


# final_rank = 5
# final_regul = 0.1
# final_iter = 20
# final_dist = 2.426742063099514
# final_alpha = 40

logger.info('Rank {0}'.format(final_rank))
logger.info('Regul {0}'.format(final_regul))
logger.info('Iter {0}'.format(final_iter))
logger.info('Dist {0}'.format(final_dist))
logger.info('Alpha {0}'.format(final_alpha))

datas.write_best_parameters(
    {'rank': final_rank, 'regul': final_regul, 'iter': final_iter, 'alpha': final_alpha},
    filename=MODEL_PARAMS_FILE_NAME,
)





