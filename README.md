# Проектная работа: Сервис рекомендаций на основе истории просмотра пользователем
[![Python version](https://img.shields.io/badge/python-v3.10-informational)](https://www.python.org)
[![Spark verions](https://img.shields.io/badge/spark-v3.3.1-informational)](https://spark.apache.org/)
[![Confluent kafka](https://img.shields.io/badge/confluent_kafka-v7.3.0-informational)](https://www.confluent.io/apache-kafka-vs-confluent/)
[![Clickhouse](https://img.shields.io/badge/clickhouse-v22.1.3-informational)](https://clickhouse.com/)
[![Airflow](https://img.shields.io/badge/airflow-v2.2.5-informational)](https://airflow.apache.org/)
[![Hadoop](https://img.shields.io/badge/hadoop-v2.0.0-informational)](https://hadoop.apache.org/)
[![Mongo](https://img.shields.io/badge/mongo-v6.0.4-informational)](https://www.mongodb.com/)
[![Grpc](https://img.shields.io/badge/grpc-v1.47.0-informational)](https://grpc.io/)
[![Nginx](https://img.shields.io/badge/nginx-v1.23.1-informational)](https://nginx.org/ru/)

[Ссылка на работу](https://github.com/xh4vm/graduate_work)

## Запуск проекта
``` 
# Копирование переменных окружения
cp .env.example .env 

# Копирование переменных окружения
cp .env.example .env 

# Копирование файлов настроек для nginx
rm -rf ./nginx/static && cp -r ./nginx/static_defaults/ ./nginx/static

# Запуск проекта
make grad
```
> После успешного запуска проекта необходимо создать connection в интерфейсе airflow (Admin -> Connections). Параметры подключения: `name: spark_default`, `host: spark-master`, `port: 7077` 

## Описание работы
Необходимо реализовать сервис по подсчету рекомендаций на основе историй просмотра. При этом необходимо учесть, что пользователь, которому необходимо предоставить рекомендации, может быть неавторизован.

**Задачи:**
- [x] Разработать архитектуру системы
- [x] Пересобрать кластер Kafka с использованием алгоритма raft
- [x] Пересобрать кластер Clickhouse с использованием алгоритма raft
- [x] Доработать API для сохранения пользовательной информации
- [x] Разработать схему таблицы кластера Clickhouse, для решения поставленной задачи
- [x] Добавить авторизацию к нодам Clickhouse
- [x] Разработать скрипт, наполняющий Clickhouse инициализационными данными
- [x] Подобрать подходящие алгоритмы для подсчета рекомендаций фильмов на основе истории просмотра (авторизованного и неавторизованного пользователя)
- [x] Выбрать подходящее хранилище данных для рекомендаций
- [x] Развернуть кластер Spark
- [x] Развернуть кластер Airflow
- [x] Развернуть кластер HDFS
- [x] Развернуть кластер MongoDB
- [x] Реализовать DAG подсчета рекомендаций
- [x] Реализовать grpc сервис выдачи рекомендаций (потенциально для сервиса выдачи контента). При этом реализовать кеширование рекомендаций для неавторизованного пользователя
- [ ] Реализовать инитер для кластера airflow
- [ ] Развернуть сервис хранения чувствительных данных: Hashi Corp Vault. Максимально уйти от использования чувствительных данных в переменных окружения

## Демонстрация
Пример развернутого сервиса представлен по адресу 130.193.38.82
[Airflow](http://130.193.38.82:8081)
[Spark](http://130.193.38.82:8080)
[Confluent Control Center](http://130.193.38.82:9021)
[Producer API](http://130.193.38.82:60666/api/openapi)
[Namenode](http://130.193.38.82:9870)
[Flower](http://130.193.38.82:5555)

## Описание сценариев Makefile
- `make grad` - установить виртуальное окружение; установить необходимые зависимости для запуска контейнеров; пересобрать контейнеры в интерактивном режиме для дипломного проекта
- `make pre-commit` - установить виртуальное окружение; установить необходимые для запуска прекоммитов зависимости; добавить статические файлы; запустить выполнение инструкций прекоммита
- `make clean-pyc` - удалить все pyc-файлы из проекта
- `make clean-all` - остановить и удалить все контейнеры и занимаемую ими память и удалить все pyc-файлы из проекта
- `make clean` - остановить и удалить контейнеры соответствующие данному проекту и занимаемую ими память и удалить все pyc-файлы из проекта
