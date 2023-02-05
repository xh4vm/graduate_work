FROM apache/airflow:2.5.1-python3.10

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential libopenmpi-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow

ARG CH_INIT_DATA_PATH=${CH_INIT_DATA_PATH}

COPY ./backend/clickhouse_initer/requirements.txt /
COPY ./backend/clickhouse_initer/src /opt/airflow/
COPY ./backend/clickhouse_initer/data/rating.csv ${CH_INIT_DATA_PATH}
RUN pip install --no-cache-dir -r /requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_HOME}"
