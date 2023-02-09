import pendulum
import redis
from airflow.decorators import dag, task

from config.base import ETL_CONFIG


@dag(
    schedule=ETL_CONFIG.ETL_MOVIE_METADATA_SCHEDULE,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["etl"],
)
def etl_from_adminpanel_to_clickhouse():
    """
    ETL процесс загрузки метаданных фильмов из админпанели в ClickHouse
    """

    @task()
    def run():
        """
        Извлечение данных из сервиса Админпанель, использую HTTP api
        """

        from storages import RedisStorage
        from storages import RunDateStorage
        from clickhouse.client import ClickhouseClient
        from extractor.http import HTTPExtractor
        from extractor.file import CSVExtractor
        from loader.clickhouse import ClickhouseLoader
        from transformer.movie import MovieTransformer

        from etl_process.etls import ETLFromAdminpanelToClickhouse

        clickhouse_client = ClickhouseClient(
            host=ETL_CONFIG.CH_CLICKHOUSE_NODE_1,
            port=ETL_CONFIG.CH_CLICKHOUSE_PORT_1,
            user="user",
            password="password",
        )

        redis_client = redis.Redis(
            host=ETL_CONFIG.REDIS_HOST, port=ETL_CONFIG.REDIS_PORT
        )

        redis_storage = RedisStorage(redis_client=redis_client)
        run_date_storage = RunDateStorage(storage=redis_storage)

        csv_extractor = CSVExtractor(file_path=ETL_CONFIG.CH_INIT_DATA_PATH, headers=['user_id', 'movie_id', 'rating'])
        movies_http_extractor = HTTPExtractor(
            api_url=ETL_CONFIG.MOVIES_ADMINPANEL_API_URL,
            run_date_storage=run_date_storage,
        )

        movies_extractor = (
            movies_http_extractor
            if ETL_CONFIG.MOVIES_ADMINPANEL_API_URL
            else csv_extractor
        )

        movie_transformer = MovieTransformer()
        movie_loader = ClickhouseLoader(client=clickhouse_client)

        etl = ETLFromAdminpanelToClickhouse(
            extractor=movies_extractor,
            transformer=movie_transformer,
            loader=movie_loader,
            store=run_date_storage,
        )

        # etl.run()
        print('Hello from ETL')

    run()


etl_from_adminpanel_to_clickhouse()