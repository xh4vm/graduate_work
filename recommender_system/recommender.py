from core.config import (BASE_DIR, SAMPLE_SIZE, SEED,
                         RANKS, REGULS, ITERS, ALPHA,
                         MODEL_PARAMS_FILE_NAME, FILE_RATING_PATH, MODEL_PARAMS)
from db.file_data_source import FileDataSet
from loguru import logger
from tqdm import tqdm
import itertools
from pyspark import SparkContext, SparkConf
from pyspark.mllib.recommendation import ALS
from metrics import get_rmse

conf = SparkConf().setAppName("Recommendation service - Recommender")
sc = SparkContext(conf=conf)
sc.setLogLevel('WARN')

datas = FileDataSet(sc, BASE_DIR)

full_ratings_data = datas.get_data(filename=FILE_RATING_PATH)
full_data_no_ratings = full_ratings_data.map(lambda x: (int(x[0]), int(x[1])))

model = ALS.trainImplicit(
    full_ratings_data,
    MODEL_PARAMS['rank'],
    MODEL_PARAMS['iter'],
    float(MODEL_PARAMS['regul']),
    alpha=float(MODEL_PARAMS['alpha'])
)

# rec_users = model.recommendProductsForUsers(30)
predictions = model.predictAll(full_data_no_ratings)
