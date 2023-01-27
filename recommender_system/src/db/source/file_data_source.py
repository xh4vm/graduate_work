import os
from pyspark.rdd import RDD
import json

from src.db.source.base import DataSet


class FileDataSet(DataSet):
    dataset_folder_path = None

    def __init__(self, context, folder_path):
        self.context = context
        self.dataset_folder_path = folder_path

    def get_data(self, *args, **kwargs) -> RDD:
        ratings_file = os.path.join(self.dataset_folder_path, kwargs['filename'])
        ratings_raw_data = self.context.textFile('file:///' + ratings_file)
        ratings_raw_data_header = ratings_raw_data.take(1)[0]
        ratings_data = ratings_raw_data.filter(lambda line: line != ratings_raw_data_header) .map(
            lambda line: line.split(",")
        ).map(
            lambda tokens: (int(tokens[0]), int(tokens[1]), int(float(tokens[2])))
        ).cache()

        return ratings_data

    def write_best_parameters(self, parameters, *args, **kwargs):

        parameters_file = os.path.join(self.dataset_folder_path, kwargs['filename'])
        json_string = json.dumps(parameters)

        with open(parameters_file, 'w') as outfile:
            outfile.write(json_string)
