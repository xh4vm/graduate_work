from config.config import SETTINGS
from vertica_worker.vertica_worker import VerticaSaver, conn_context_vertica


def main():
    with (
        conn_context_vertica(SETTINGS.VERTICA.dict()) as connection
    ):
        for table_name in SETTINGS.TABLES.keys():
            VerticaSaver(connection).execute_sql_command(""" DROP TABLE {0};""".format(table_name))


if __name__ == '__main__':
    main()
