import datetime
import json
from pathlib import Path

from loguru import logger

from adapters.clickhouse.client import ClickHouseClient
from settings import olap_research_settings

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

db_client = ClickHouseClient(host="localhost", port="9000")


def run_query(query_object):
    logger.info("Запрос: %s" % query_object.get("name"))
    logger.info("Текст: %s" % query_object.get("query")[:120])
    start = datetime.datetime.now()
    r = db_client.execute(query_object.get("query"))
    logger.info("result: %s" % str(r))
    logger.info("time: %s" % str(datetime.datetime.now() - start))


queries_path = olap_research_settings.OLAP_RESEARCH_QUERIES_PATH
if queries_path.startswith("/"):
    queries_path = queries_path[1:]

with open(ROOT_DIR / queries_path) as f:
    queries = json.load(f)
    for query in queries:
        run_query(query)
