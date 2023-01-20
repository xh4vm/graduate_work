from contextlib import contextmanager
from datetime import datetime, timedelta

import backoff
import vertica_python
from loguru import logger
from utility.utility import get_time
from vertica_python import Connection, DatabaseError, OperationalError


class VerticaSaver:
    sql_time = timedelta(0)
    """Class for work with Vertica."""

    def __init__(
            self, connection: Connection,
            tables: dict = None,
            truncate: bool = True,
            batch_size: int = 1000,
            connect_params: dict = None,
    ):
        """Init class object.

        Arguments:
            connection: connection to database Vertica.
            truncate: flag setting the need to truncate tables
            batch_size: size of the stack of records to upload to the table.
            tables: tables dictionary
        """
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.batch_size = batch_size
        self.truncate = truncate
        self.tables = tables
        self.error = None
        self.connect_params = connect_params

    def connect(self):
        self.connection = vertica_python.connect(**self.connect_params)
        self.cursor = self.connection.cursor()

    @backoff.on_exception(
        backoff.expo, (ConnectionRefusedError, OperationalError), max_tries=10
    )
    @get_time
    def execute_sql_command(self, query: str) -> bool:
        """Execute command in database.

        Arguments:
            query: text query for execute
        """

        if not self.connection:
            self.connect()
        try:
            self.cursor.execute(query)
        except DatabaseError as err:
            self.error = err
            logger.error(err)
            return False

        return True

    def truncate_table(self, table_name):
        self.execute_sql_command('TRUNCATE TABLE {0};'.format(table_name))

    @backoff.on_exception(
        backoff.expo, (ConnectionRefusedError, OperationalError), max_tries=10
    )
    def save_table_to_vertica(self, table_name: str, dataset):
        """Load data to vertica.

        Arguments:
            table_name: name of table
            dataset: data for save
        """
        if not self.connection:
            self.connect()

        query = """INSERT INTO {0}({1}) VALUES ({2})""".format(
            table_name,
            ', '.join(self.tables[table_name]['names']),
            ', '.join(['%s'] * len(self.tables[table_name]['names']))
        )
        try:
            start_time = datetime.now()
            self.cursor.executemany(query, dataset, use_prepared_statements=False)
            self.sql_time += (datetime.now() - start_time)
        except DatabaseError as err:
            self.error = err
            logger.error(err)
            return False

        self.connection.commit()
        return True


@contextmanager
def conn_context_vertica(db_vertica: dict) -> Connection:
    """Context manager for Vertica database."""

    connection = vertica_python.connect(**db_vertica)

    yield connection

    connection.close()
