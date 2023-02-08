from typing import Iterable, Any, Dict, List
from extract.base import BaseExtractor
from pathlib import Path
import csv


class CSVExtractor(BaseExtractor):

    def __init__(self, file_path: str, headers: List[str], with_headers: bool = True) -> None:
        self.file_path: Path = Path(file_path)
        self.headers = headers
        self.with_headers = with_headers

    def extract(self) -> Iterable[Dict[str, Any]]: # need for python 3.8
        if not self.file_path.is_file():
            raise ValueError('File not found')

        with open(self.file_path, 'r') as fd:
            reader = csv.reader(fd)
            
            if self.with_headers:
                next(reader)

            for line in reader:
                yield {key: line[i] for i, key in enumerate(self.headers)}
