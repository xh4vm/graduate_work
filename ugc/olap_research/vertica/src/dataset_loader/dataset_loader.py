import os
from dataclasses import dataclass

from pandas import read_csv


@dataclass
class DatasetLoader:
    batch_size: int
    dataset_folder: str
    dataset_file_ext: str
    dataset_data_deliver: str
    dataset_data_skip_row: int
    file_name = ''
    column_types: dict = None
    error = None

    def load_batch(self):
        for batch in read_csv(
                self.file_name,
                engine='python',
                sep=self.dataset_data_deliver,
                header=None,
                skiprows=self.dataset_data_skip_row,
                chunksize=self.batch_size,
                dtype=self.column_types,
        ):
            yield [tuple(value) for value in batch.values.tolist()]

    def prepare_to_loading(self, file_name: str, types: dict):
        path_file = os.sep.join([self.dataset_folder, '{0}.{1}'.format(file_name, self.dataset_file_ext)])
        if not os.path.exists(path_file):
            self.error = 'The file {0} does not exist.'.format(path_file)
            return False
        self.file_name = path_file
        self.column_types = types
        return True
