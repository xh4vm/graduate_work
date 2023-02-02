from celery import Celery

from celery.schedules import crontab
from src.core.config import SETTINGS
from loguru import logger
from src.recommender import start_prepare_data
from src.mongodb_test import mongodb_test
from src.clickhouse_test import clickhouse_test


celery = Celery(SETTINGS.celery.name, backend=SETTINGS.celery.backend, broker=SETTINGS.celery.broker)


@celery.task
def task_prepare_data():
    start_prepare_data()


@celery.on_after_configure.connect
def setup_recommendations_periodic_task(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=1, minute=30),
        task_prepare_data.s(),
        name='Update recommendations every day.',
    )


@celery.task
def task_connectors_test():
    logger.info('Test MONGODB connector')
    mongodb_test()
    # logger.info('Test CLICKHOUSE connector')
    # clickhouse_test()


@celery.on_after_configure.connect
def setup_task_mongodb_connector_test(sender, **kwargs):
    sender.add_periodic_task(60.0, task_connectors_test.s(), name='TEST Connectors every 600s.')


# @celery.task
# def hello_celery():
#     logger.info('Hello')
#
#
# @celery.on_after_configure.connect
# def hello_task(sender, **kwargs):
#     sender.add_periodic_task(30.0, hello_celery.s(), name='Print Hello every 30s.')
