from dataclasses import dataclass
from datetime import datetime

from etl_process.base import BaseETL
from loguru import logger

from extractor.base import BaseExtractor
from loader.base import BaseLoader
from storages import RunDateStorage
from transformer.base import BaseTransformer


@dataclass
class ETLFromAdminpanelToClickhouse(BaseETL):
    extractor: BaseExtractor
    transformer: BaseTransformer
    loader: BaseLoader
    store: RunDateStorage

    def run(self):
        logger.info("[*] Extract movie metadata")
        extracted_data_generator = self.extractor.extract()
        logger.info("[+] Successfull extract movie metadata")

        logger.info("[*] Transform movie metadata")
        transformed_data = self.transformer.transform(extracted_data_generator)
        logger.info("[+] Successfull transform movie metadata")

        logger.info("[*] Load movie metadata")
        response = self.loader.insert(data=transformed_data, table="default.movie_meta")
        if response:
            self.store.set_run_date(datetime.now())
            logger.info("[+] Successfull load movie metadata")
