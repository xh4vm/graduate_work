# Проектная работа 8 спринта

[Ссылка на работу](https://github.com/xh4vm/ugc)

Проектные работы в этом модуле выполняются в командах по 3 человека. Процесс обучения аналогичен сервису, где вы изучали асинхронное программирование. Роли в команде и отправка работы на ревью не меняются.

Распределение по командам подготовит команда сопровождения. Куратор поделится с вами списками в Slack в канале #group_projects.

Задания на спринт вы найдёте внутри тем.

## Исследование OLAP-хранилища
В рамках данного модуля было проведено исследование OLAP хранилища (clickhouse и vertica). Сводные результаты можно найти в [директории](https://github.com/xh4vm/ugc/tree/main/olap_research). Результаты по каждому хранилищу можно найти в директориях:
- [./olap_research/clickhouse](https://github.com/xh4vm/ugc/tree/main/olap_research/clickhouse)
- [./olap_research/vertica](https://github.com/xh4vm/ugc/tree/main/olap_research/vertica)

В рамках данного модуля в качестве OLAP хранилища выбран ClickHouse

## Запуск сервиса аналитики
```
# Установка файлов переменных окружения
cp .env.example .env 

# Подготовка файлов-логов nginx
rm -rf ./backend/nginx/static && cp -r ./backend/nginx/static_defaults/ ./backend/nginx/static

# Запуск проекта
make ugc
```

## Управление проектом 
Осуществлялось в [notion](https://obtainable-stinger-44c.notion.site/1fb8cf0aecb348b5b56f03c59865be3a?v=605f36748e354f83b93182ffccffff16)

## Документация
#### API
http://localhost:60666/api/openapi

## Пример рабочего токена авторизации (примерно на 10 лет): 
X-Authorization-Token: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicGVybWlzc2lvbnMiOnsiMDM3YWJkMDI2M2JlNTg2OWMzNzZjZjU5ODlhMTQ4YTAiOlsiR0VUIiwiUE9TVCJdfSwiZXhwIjoxNjcwOTI1MDg0LCJpYXQiOjE2Njk5MjUwODR9.MiR0CEaNXpTZfVk5-T67sWUNrhGpMTf8GNhbhfuBzyE"
