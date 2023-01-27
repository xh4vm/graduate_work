from math import sqrt
from operator import add


def get_rmse(actual, size_actual, predictions):
    predictions_and_ratings = predictions.join(actual).values()
    return sqrt(predictions_and_ratings.map(lambda s: (s[0] - s[1]) ** 2).reduce(add) / float(size_actual))
