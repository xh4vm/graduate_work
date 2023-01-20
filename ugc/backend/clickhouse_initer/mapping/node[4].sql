CREATE DATABASE IF NOT EXISTS movies;
CREATE DATABASE IF NOT EXISTS movies_replica;

CREATE TABLE IF NOT EXISTS movies.movie_frame_queue
(
    movie_id          String,
    frame_time        Int64
)
ENGINE=Kafka()
SETTINGS
kafka_broker_list = 'kafka01:9092,kafka02:9092,kafka03:9092',
kafka_topic_list = 'movie_frame',
kafka_group_name = 'movie_frame_group1',
kafka_format = 'AvroConfluent',
format_avro_schema_registry_url = 'http://schema-registry:8081';


CREATE TABLE IF NOT EXISTS movies_replica.movie_frame
(
    id                UUID,
    user_id           String,
    movie_id          String,
    frame_time        Int64,
    event_time        DateTime  DEFAULT now()
)
Engine=ReplicatedMergeTree('/clickhouse/tables/shard2/movie_frame', 'replica4')
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (id);


CREATE MATERIALIZED VIEW IF NOT EXISTS movies.movie_frame_consumer
TO movies.movie_frame
AS SELECT movie_id, frame_time, _key as user_id, generateUUIDv4() as id
FROM movies.movie_frame_queue;


CREATE TABLE IF NOT EXISTS default.movie_frame
(
    id                UUID,
    user_id           String,
    movie_id          String,
    frame_time        Int64,
    event_time        DateTime
)
ENGINE = Distributed('main_cluster', '', movie_frame, rand());
