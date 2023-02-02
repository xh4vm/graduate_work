# Проектная работа: диплом

[Ссылка на работу](https://github.com/xh4vm/graduate_work)

## Запуск проекта
``` 
# Копирование переменных окружения
cp .env.example .env 

# Копирование переменных окружения для сервиса ugc
cp ./ugc/.env.example ./ugc/.env 

# Копирование переменных окружения для сервиса recommender_system
cp ./recommender_system/.env.example ./recommender_system/.env 
# Создание файлов логов для celery
rm -rf ./recommender_system/log && mkdir ./recommender_system/log && echo CELERY_BEAT_LOGS > ./recommender_system/log/celery_beat.log

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
