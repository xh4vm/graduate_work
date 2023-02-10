import airflow
from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator 

default_args = {
    'owner': 'airflow',    
    'retry_delay': timedelta(minutes=5),
}

dag_movie_frame_recommender_system = DAG(
        dag_id = 'dag_movie_frame_recommender_system',
        default_args=default_args,
        schedule_interval=None,	
        dagrun_timeout=timedelta(minutes=60),
        description='Рекомендательная система фильмов на основе истории просмотра пользователя',
        start_date = airflow.utils.dates.days_ago(1)
)

# etl_clickhouse_to_parquet = SparkSubmitOperator(
#     application='/opt/airflow/dags/movie_frame/etl_clickhouse_to_parquet.py',
#     conn_id='spark_default',
#     verbose=1,
#     task_id='etl_clickhouse_to_parquet',
#     dag=dag_movie_frame_recommender_system
# )
#
# etl_admin_api_to_parquet = SparkSubmitOperator(
#     application='/opt/airflow/dags/movie_frame/etl_admin_api_to_parquet.py',
#     conn_id='spark_default',
#     verbose=1,
#     task_id='etl_admin_api_to_parquet',
#     dag=dag_movie_frame_recommender_system
# )
#
# etl_join_data = SparkSubmitOperator(
#     application='/opt/airflow/dags/movie_frame/etl_join_data.py',
#     conn_id='spark_default',
#     verbose=1,
#     task_id='etl_join_data',
#     dag=dag_movie_frame_recommender_system
# )
#
# als = SparkSubmitOperator(
#     application='/opt/airflow/dags/movie_frame/als.py',
#     conn_id='spark_default',
#     verbose=1,
#     task_id='als',
#     dag=dag_movie_frame_recommender_system
# )
#
# load_to_mongo = SparkSubmitOperator(
#     application='/opt/airflow/dags/movie_frame/load_to_mongo.py',
#     conn_id='spark_default',
#     verbose=1,
#     task_id='load_to_mongo',
#     dag=dag_movie_frame_recommender_system
# )
#
# [etl_admin_api_to_parquet, etl_clickhouse_to_parquet] >> etl_join_data >> als >> load_to_mongo

movie_frame_recommender_system_etl_job = SparkSubmitOperator(
    application='/opt/airflow/dags/movie_frame_recommender_system_etl_job.py',
    conn_id='spark_default',
    verbose=1,
    task_id='movie_frame_recommender_system_etl_job',
    dag=dag_movie_frame_recommender_system
)

movie_frame_recommender_system_etl_job
