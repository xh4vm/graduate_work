from config.nodes import NODES
from config.base import CLICKHOUSE_CONFIG
from config.logger import logger
from clickhouse.client import ClickhouseClient
from clickhouse.loader import ClickhouseLoader
from extractor.file import CSVExtractor
from transformer.movie_frame import MovieFrameTransformer


if __name__ == '__main__':

    for NODE in NODES:
        logger.info('[*] Start creating mapping')

        ch_initer = ClickhouseClient(host=NODE.HOST, port=NODE.PORT,
            user='user', password='password')
        ch_initer.create(ddl_file=f'./mapping/{NODE.SCHEMA_NAME}')

    if CLICKHOUSE_CONFIG.INIT_DATA and CLICKHOUSE_CONFIG.INIT_DATA_PATH is not None:
        logger.info('[*] Start init data')
        logger.info('[*] Connecting into clickhouse')
        
        client = ClickhouseClient(host=NODES[0].HOST, port=NODES[0].PORT,
            user='user', password='password')
    
        extractor = CSVExtractor(file_path=CLICKHOUSE_CONFIG.INIT_DATA_PATH, headers=['user_id', 'movie_id', 'rating'])
        transformer = MovieFrameTransformer()
        loader = ClickhouseLoader(client=client)

        logger.info('[*] Extract data')
        raw_data = extractor.extract()
        logger.info('[+] Successfull extract data')

        logger.info('[*] Transform data')
        transformed_data = transformer.transform(raw_data)
        logger.info('[+] Successfull transform data')
        
        logger.info('[*] Load data')
        loader.insert(table=CLICKHOUSE_CONFIG.INIT_TABLE, data=transformed_data)
        logger.info('[+] Successfull load data')
