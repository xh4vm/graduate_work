CREATE DATABASE IF NOT EXISTS movies;
CREATE DATABASE IF NOT EXISTS movies_replica;

CREATE TABLE IF NOT EXISTS movies.movie_frame_queue
(
    movie_id                  String,
    frame_time                Int64,
    `event.type`              String,
    `event.timestamp`         Int64,
    `event.generated_after`   Int64
)
ENGINE=Kafka()
SETTINGS
kafka_broker_list = 'kafka01:9092,kafka02:9092,kafka03:9092',
kafka_topic_list = 'movie_frame',
kafka_group_name = 'movie_frame_group1',
kafka_format = 'JSONEachRow',
input_format_import_nested_json=1;


CREATE TABLE IF NOT EXISTS movies.movie_frame
(
    id                      UUID,
    user_id                 String,
    movie_id                String,
    frame_time              Int64,
    event_type              String,
    event_timestamp         Int64,
    event_generated_after   Int64,
    created_at              DateTime  DEFAULT now()
)
Engine=ReplicatedMergeTree('/clickhouse/tables/shard1/movie_frame', 'replica3')
PARTITION BY toYYYYMMDD(created_at)
ORDER BY (id);


CREATE MATERIALIZED VIEW IF NOT EXISTS movies.movie_frame_consumer
TO movies.movie_frame
AS SELECT movie_id, frame_time, _key as user_id, generateUUIDv4() as id, event.type as event_type, event.timestamp as event_timestamp, event.generated_after as event_generated_after
FROM movies.movie_frame_queue;


CREATE TABLE IF NOT EXISTS default.movie_frame
(
    id                      UUID,
    user_id                 String,
    movie_id                String,
    frame_time              Int64,
    event_type              String,
    event_timestamp         Int64,
    event_generated_after   Int64,
    created_at              DateTime  DEFAULT now()
)
ENGINE = Distributed('main_cluster', '', movie_frame, rand());
