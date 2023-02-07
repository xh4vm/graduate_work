ARG CH_SERVER_IMG_VER
FROM yandex/clickhouse-server:${CH_SERVER_IMG_VER}

COPY ./clickhouse/server_config /etc/clickhouse-server
COPY ./clickhouse/server_config/metrika.xml /etc/metrika.xml

COPY ./clickhouse/server_config/enable_keeper.xml /etc/clickhouse-server/config.d/enable_keeper.xml
