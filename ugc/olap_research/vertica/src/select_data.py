from config.config import SETTINGS, SQL_QUERY
from loguru import logger
from vertica_worker.vertica_worker import VerticaSaver, conn_context_vertica


def select_data(conn):
    vertica = VerticaSaver(conn)
    for name, execute_sql_command in SQL_QUERY.items():
        logger.info(name)
        vertica.execute_sql_command(execute_sql_command)


def main():
    with (
        conn_context_vertica(SETTINGS.VERTICA.dict()) as connection
    ):
        select_data(connection)


if __name__ == '__main__':
    main()
