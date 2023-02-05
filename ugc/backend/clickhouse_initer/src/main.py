import redis

from clickhouse.client import ClickhouseClient
from clickhouse.loader import ClickhouseLoader
from config.base import CLICKHOUSE_CONFIG, ETL_CONFIG
from config.logger import logger
from config.nodes import NODES
from etl.etls import ETLFromAdminpanelToClickhouse
from extractor.file import CSVExtractor
from extractor.http import HTTPExtractor
from storages import RunDateStorage, RedisStorage
from transformer.movie import MovieTransformer
from transformer.movie_frame import MovieFrameTransformer

clickhouse_client = ClickhouseClient(
    host=NODES[0].HOST, port=NODES[0].PORT, user="user", password="password"
)
csv_extractor = CSVExtractor(
    file_path=CLICKHOUSE_CONFIG.INIT_DATA_PATH,
    headers=["user_id", "movie_id", "rating"],
)

if __name__ == "__main__":

    for NODE in NODES:
        logger.info("[*] Start creating mapping")

        ch_initer = ClickhouseClient(
            host=NODE.HOST, port=NODE.PORT, user="user", password="password"
        )
        ch_initer.create(ddl_file=f"./mapping/{NODE.SCHEMA_NAME}")

    if CLICKHOUSE_CONFIG.INIT_DATA and CLICKHOUSE_CONFIG.INIT_DATA_PATH is not None:
        logger.info("[*] Start init data")
        logger.info("[*] Connecting into clickhouse")

        transformer = MovieFrameTransformer()
        loader = ClickhouseLoader(client=clickhouse_client)

        logger.info("[*] Extract data")
        raw_data = csv_extractor.extract()
        logger.info("[+] Successfull extract data")

        logger.info("[*] Transform data")
        transformed_data = transformer.transform(raw_data)
        logger.info("[+] Successfull transform data")

        logger.info("[*] Load data")
        loader.insert(data=transformed_data, table=CLICKHOUSE_CONFIG.INIT_TABLE)
        logger.info("[+] Successfull load data")

        # redis_client = redis.Redis(
        #     host=ETL_CONFIG.REDIS_HOST, port=ETL_CONFIG.REDIS_PORT
        # )
        # redis_storage = RedisStorage(redis_client=redis_client)
        # run_date_storage = RunDateStorage(storage=redis_storage)
        # movies_http_extractor = HTTPExtractor(
        #     api_url=ETL_CONFIG.MOVIES_ADMINPANEL_API_URL,
        #     run_date_storage=run_date_storage,
        # )
        # movies_extractor = (
        #     movies_http_extractor
        #     if ETL_CONFIG.MOVIES_ADMINPANEL_API_URL
        #     else csv_extractor
        # )
        #
        # movie_transformer = MovieTransformer()
        # movie_loader = ClickhouseLoader(client=clickhouse_client)
        #
        # etl_from_adminpanel_to_clickhouse = ETLFromAdminpanelToClickhouse(
        #     extractor=movies_extractor,
        #     transformer=movie_transformer,
        #     loader=movie_loader,
        #     store=run_date_storage,
        # )
        #
        # # TODO: переделать запуск ETL на cron
        # etl_from_adminpanel_to_clickhouse.run()
