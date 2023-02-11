import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 

from src.core.config import AIRFLOW_DAG_MOVIE_FRAME_CONFIG


default_args = {
    'owner': 'airflow',    
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
}

# AIRFLOW_DAG_MOVIE_FRAME_CONFIG.TUNE_ALS_SCHEDULE

dag_movie_frame_tune_als_recommender_system = DAG(
        dag_id='dag_movie_frame_tune_als_recommender_system',
        default_args=default_args,
        dagrun_timeout=timedelta(minutes=60),
        description='Настройка параметров ALS модели рекомендательная система фильмов на основе истории просмотра пользователя',
        schedule=None,
        start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
        catchup=False,
        tags=['movie_frame'],
)

etl_clickhouse_to_parquet = SparkSubmitOperator(
    application='/opt/airflow/dags/movie_frame/etl_clickhouse_to_parquet.py',
    conn_id='spark_default',
    verbose=1,
    task_id='etl_clickhouse_to_parquet',
    dag=dag_movie_frame_tune_als_recommender_system
)

etl_admin_api_to_parquet = SparkSubmitOperator(
    application='/opt/airflow/dags/movie_frame/etl_admin_api_to_parquet.py',
    conn_id='spark_default',
    verbose=1,
    task_id='etl_admin_api_to_parquet',
    dag=dag_movie_frame_tune_als_recommender_system
)

etl_join_data = SparkSubmitOperator(
    application='/opt/airflow/dags/movie_frame/etl_join_data.py',
    conn_id='spark_default',
    verbose=1,
    task_id='etl_join_data',
    dag=dag_movie_frame_tune_als_recommender_system
)

tune_als = SparkSubmitOperator(
    application='/opt/airflow/dags/movie_frame/tune_als.py',
    conn_id='spark_default',
    verbose=1,
    task_id='tune_als',
    dag=dag_movie_frame_tune_als_recommender_system
)

[etl_admin_api_to_parquet, etl_clickhouse_to_parquet] >> etl_join_data >> tune_als
