from dataclasses import dataclass
from typing import Any, Iterable

import backoff
import requests
from loguru import logger

from extractor.base import BaseExtractor
from storages import RunDateStorage


@dataclass
class HTTPExtractor(BaseExtractor):
    run_date_storage: RunDateStorage
    api_url: str = ""

    def extract(self) -> Iterable[dict[str, Any]]:
        url = self.api_url
        while url:
            results = ()
            logger.info("[*] Extract movie metadata via http")
            response_json = self.send_request(url)
            if response_json:
                url = response_json.get("next")
                results = response_json.get("results") or ()
                logger.info("[+] Successfull extract movie metadata via http")
            else:
                url = None
                logger.info("[-] An error occurred while extracting movie metadata via http")
            for movie in results:
                yield movie

    @backoff.on_exception(wait_gen=backoff.expo, exception=Exception, max_tries=8, raise_on_giveup=False)
    def send_request(self, url):
        params = {"updated": self.run_date_storage.get_run_date()}
        response = requests.get(url, params=params)
        return response.json()
