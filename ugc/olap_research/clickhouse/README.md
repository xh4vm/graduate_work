# Исследование времени выполнения запросов на вставку и чтения записей в OLAP системе

## ClickHouse

### Параметры кластера
* Количество шардов: 2
* Количество реплик: по 2 на шард
* Итого серверов: 4

### Загрузка в БД
Всего строк: 25000096

| Размер пачки | Общее время    | Только SQL     | Всего пачек | Время вставки пачки, с | Post обработка                              |
|--------------|----------------|----------------|-------------|------------------------|---------------------------------------------|
| 1k           | 0:03:57.208066 | 0:01:43.379796 | 25.025      | 00.004                 | ещё что-то происходит в течении 10-15 минут |
| 10k          | 0:01:39.992519 | 0:00:21.290871 | 2500        | 00.009                 | ещё что-то происходит в течении  2-3 минут  |
| 100k         | 0:01:06.063562 | 0:00:12.258034 | 250         | 00.05                  | -                                           |
| 1m           | 0:01:00.809838 | 0:00:12.690288 | 25          | 00.51                  | -                                           |
| 10m          | 0:01:00.462915 | 0:00:10.657789 | 2           | 5.33                   | -                                           |
| 10m + чтение | 0:01:57.719340 | 0:00:23.222058 | 2           | 11.61                  | -                                           |


### Выборка из БД

| Выборка | Время выборки  | Время выборки + запись |
|---------|----------------|------------------------|
| 1       | 0:00:00.200286 | 0:00:00.335691         |
| 2       | 0:00:00.185560 | 0:00:00.320043         |
| 3       | 0:00:00.273478 | 0:00:00.449501         |
| 4       | 0:00:03.717096 | 0:00:06.853634         |
| 5       | 0:00:06.197345 | 0:00:09.917351         |


```Выборка 1
SELECT movie_id, COUNT(*) movie_count FROM views_progress GROUP BY movie_id ORDER BY movie_count DESC LIMIT 20;
```

```Выборка 2
SELECT COUNT(*) FROM (SELECT movie_id, COUNT(*) movie_count FROM views_progress GROUP BY movie_id) as view_movie_counter WHERE movie_count<10
```

```Выборка 3
SELECT movie_id, sum(movie_frame) as sum_movie_frame FROM views_progress GROUP BY movie_id ORDER BY sum_movie_frame DESC LIMIT 20
```

```Выборка 4
SELECT user_id, count(*) as movies_count FROM (SELECT DISTINCT user_id, movie_id FROM views_progress GROUP BY user_id, movie_id) as view_user_movie GROUP BY user_id ORDER BY movies_count DESC LIMIT 20
```

```Выборка 5
SELECT user_id, SUM(max_user_movie_frame) as total_user_movies_frame FROM (SELECT DISTINCT user_id, movie_id, MAX(movie_frame) as max_user_movie_frame FROM views_progress GROUP BY user_id, movie_id) as view_user_movie GROUP BY user_id ORDER BY total_user_movies_frame DESC LIMIT 20
```
