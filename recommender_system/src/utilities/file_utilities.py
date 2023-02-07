import json
import os


def get_data_from_file(file_path):
    with open(file_path) as income_file:
        return income_file.read()


def get_data_from_json(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)


def write_best_parameters(parameters, file_path):

    parameters_file = os.path.join(file_path)
    json_string = json.dumps(parameters)

    with open(parameters_file, 'w') as outfile:
        outfile.write(json_string)
