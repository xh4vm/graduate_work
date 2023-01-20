# Исследование времени выполнения запросов на вставку и чтения записей в OLAP системе

## Vertica
Single-mode
В каталог src/dataset необходимо поместить файл views_progress.csv с данными для загрузки. В формат: userId,movieId,rating,timestamp

### Загрузка в БД
Всего строк: 25000096

| Размер пачки | Общее время    | Только SQL     | Всего пачек | Время вставки пачки, с | Post обработка                              |
|--------------|----------------|----------------|-------------|------------------------|---------------------------------------------|
| 1k           |   > 3 часов    | -              | 25.025      | -                      |                                             |
| 10k          | 0:48:43.219346 | 0:05:41.028316 | 2500        | 00.14                  |                                             |
| 100k         | 0:09:22.708373 | 0:03:34.829867 | 250         | 00.86                  | -                                           |
| 1m           | 0:05:54.266007 | 0:03:29.358591 | 25          | 08.36                  | -                                           |
| 10m          | 0:05:38.287020 | 0:03:29.044678 | 2           | 104.5                  | -                                           |
| 1m + чтение  | 0:10:46.535976 | 0:06:13.940257 | 2           | 14.96                  | -                                           |
  

### Выборка из БД

| Выборка | Время выборки  | Время выборки + запись |
|---------|----------------|------------------------|
| 1       | 0:00:01.089865 | 0:00:02.155945         |
| 2       | 0:00:00.944607 | 0:00:02.217880         |
| 3       | 0:00:01.025218 | 0:00:02.022981         |
| 4       | 0:00:09.013853 | 0:00:15.366936         |
| 5       | 0:00:09.764115 | 0:00:17.715298         |


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

