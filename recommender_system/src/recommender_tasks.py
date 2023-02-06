from celery import Celery
from celery.schedules import crontab
from src.core.config import SETTINGS
from src.recommender import start_prepare_data


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


# @celery.task
# def task_clickhouse_test():
#     logger.info('Test CLICKHOUSE connector')
#     clickhouse_test()
#     logger.info('END Test CLICKHOUSE connectors')
#
#
# @celery.on_after_configure.connect
# def setup_task_clickhouse_connector_test(sender, **kwargs):
#     sender.add_periodic_task(60.0, task_clickhouse_test.s(), name='TEST Connectors every 600s.')
#
#
# @celery.task
# def task_mongodb_test():
#     logger.info('START Test MONGODB connectors')
#     mongodb_test()
#     logger.info('END Test MONGODB connectors')
#
#
# @celery.on_after_configure.connect
# def setup_task_mongodb_connector_test(sender, **kwargs):
#     sender.add_periodic_task(60.0, task_mongodb_test.s(), name='TEST Connectors every 600s.')
#
#
# @celery.task
# def task_clickhouse_mongodb_serially_test():
#     logger.info('Test CLICKHOUSE connector')
#     clickhouse_test()
#     logger.info('END Test CLICKHOUSE connectors')
#     logger.info('START Test MONGODB connectors')
#     mongodb_test()
#     logger.info('END Test MONGODB connectors')
#
#
# @celery.on_after_configure.connect
# def setup_task_clickhouse_mongodb_connectors_serially_test(sender, **kwargs):
#     sender.add_periodic_task(60.0, task_clickhouse_mongodb_serially_test.s(), name='TEST Connectors every 600s.')
#
#
# @celery.task
# def task_clickhouse_mongodb_together_test():
#     logger.info('Test CLICKHOUSE and MONGODB connectors together')
#     mongodb_with_clickhouse_together_test()
#     logger.info('END Test CLICKHOUSE and MONGODB connectors together')
#
#
# @celery.on_after_configure.connect
# def setup_task_clickhouse_mongodb_connectors_together_test(sender, **kwargs):
#     sender.add_periodic_task(60.0, task_clickhouse_mongodb_together_test.s(), name='TEST Connectors every 600s.')
