from datetime import datetime

from config.config import SETTINGS
from dataset_loader.dataset_loader import DatasetLoader
from loguru import logger
from utility.utility import get_time
from vertica_python import Connection
from vertica_worker.vertica_worker import VerticaSaver, conn_context_vertica


def transform_data(data):
    res = [(value[0], value[1], value[3], datetime.now()) for value in data]
    return res


@get_time
def load_data_to_vertica(conn: Connection):
    """The main method of loading data from SQLite to Postgres."""

    vertica_saver = VerticaSaver(
        conn,
        SETTINGS.TABLES,
        SETTINGS.TRUNCATE_TABLE,
        SETTINGS.BATCH_SIZE,
        SETTINGS.VERTICA.dict(),
    )

    dataset_loader = DatasetLoader(
        SETTINGS.BATCH_SIZE,
        SETTINGS.DATASET_FOLDER,
        SETTINGS.DATASET_FILE_EXT,
        SETTINGS.DATASET_DATA_DELIVER,
        SETTINGS.DATASET_DATA_SKIP_ROW,
    )

    # Create tables
    if SETTINGS.CREATE_TABLE:
        sql = open(SETTINGS.DDL_FILE, "r").read()
        vertica_saver.execute_sql_command(sql)
        vertica_saver.connection.commit()

    for table_name, value in SETTINGS.TABLES.items():

        if not dataset_loader.prepare_to_loading(table_name, value['types']):
            logger.error(dataset_loader.error)
            continue

        if SETTINGS.TRUNCATE_TABLE and not vertica_saver.truncate_table(table_name):
            logger.error(vertica_saver.error)
            break

        batch_data_generator = dataset_loader.load_batch()
        for batch_number, batch_data in enumerate(batch_data_generator, 1):
            data_to_load = transform_data(batch_data)
            logger.info('Пачка №{0}'.format(batch_number))
            if not vertica_saver.save_table_to_vertica(table_name, data_to_load):
                logger.error(vertica_saver.error)
                break

    return vertica_saver.sql_time


def main():
    with (
        conn_context_vertica(SETTINGS.VERTICA.dict()) as connection
    ):
        sql_time = load_data_to_vertica(connection)
        logger.info('Время выполнения SQL: {0}s'.format(sql_time))


if __name__ == '__main__':
    main()
