CREATE STREAM IF NOT EXISTS `movie-frame-stream`(
    `user_id` VARCHAR KEY,
    `movie_id` VARCHAR,
    `frame_time` INT,
    `event` STRUCT<
        `type` VARCHAR,
        `timestamp` INT,
        `generated_after` INT
    >
) WITH (kafka_topic='movie_frame', value_format='json');


CREATE TABLE IF NOT EXISTS `movie-viewed-time` WITH(KEY_FORMAT='JSON') AS
    SELECT 
        `user_id`,
        `movie_id`,
        SUM(
            CASE
                WHEN `event`->`type` = 'starting' THEN -1 * `frame_time`
                WHEN `event`->`type` = 'stopped' THEN `frame_time`
                ELSE 0
            END
        ) AS `with_last_stop`,
        SUM(`event`->`generated_after`) AS `viewed_process`
    FROM `movie-frame-stream`
    GROUP BY `user_id`, `movie_id`;
