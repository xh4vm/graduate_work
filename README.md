# Проектная работа: диплом
[![Python version](https://img.shields.io/badge/python-3.10-informational)](https://www.python.org)
[![Spark verions](https://img.shields.io/badge/spark-3.3.1-informational)](https://spark.apache.org/)
[![Confluent kafka](https://img.shields.io/badge/confluent_kafka-7.3.0-informational)](https://www.confluent.io/apache-kafka-vs-confluent/)
[![Clickhouse](https://img.shields.io/badge/clickhouse-22.1.3-informational)](https://clickhouse.com/)
[![Airflow](https://img.shields.io/badge/airflow-2.2.5-informational)](https://airflow.apache.org/)
[![Hadoop](https://img.shields.io/badge/hadoop-2.0.0-informational)](https://hadoop.apache.org/)
[![Mongo](https://img.shields.io/badge/mongo-6.0.4-informational)](https://www.mongodb.com/)
[![Grpc](https://img.shields.io/badge/grpc-1.47.0-informational)](https://grpc.io/)
[![Nginx](https://img.shields.io/badge/nginx-1.23.1-informational)](https://nginx.org/ru/)

[Ссылка на работу](https://github.com/xh4vm/graduate_work)

## Запуск проекта
``` 
# Копирование переменных окружения
cp .env.example .env 

# Копирование переменных окружения для сервиса ugc
cp ./ugc/.env.example ./ugc/.env 

# Копирование переменных окружения для сервиса recommender_system
cp ./recommender_system/.env.example ./recommender_system/.env 

# Копирование файлов настроек для nginx
rm -rf ./nginx/static && cp -r ./nginx/static_defaults/ ./nginx/static

# Запуск проекта
make grad
```

## Описание сценариев Makefile
- `make grad` - установить виртуальное окружение; установить необходимые зависимости для запуска контейнеров; пересобрать контейнеры в интерактивном режиме для дипломного проекта
- `make pre-commit` - установить виртуальное окружение; установить необходимые для запуска прекоммитов зависимости; добавить статические файлы; запустить выполнение инструкций прекоммита
- `make clean-pyc` - удалить все pyc-файлы из проекта
- `make clean-all` - остановить и удалить все контейнеры и занимаемую ими память и удалить все pyc-файлы из проекта
- `make clean` - остановить и удалить контейнеры соответствующие данному проекту и занимаемую ими память и удалить все pyc-файлы из проекта
