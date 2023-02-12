FROM python:3.8-slim AS airflow-builder

WORKDIR /opt
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends build-essential python-dev python3-dev g++ \
     && pip install --upgrade pip \
     && pip install wheel && pip3 wheel -r requirements.txt --wheel-dir=/opt/wheels

FROM apache/airflow:2.2.5-python3.8

USER root
COPY --from=airflow-builder /opt /opt

RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow
ENV PYTHONPATH /opt/airflow/:/opt/airflow/src/:/opt/airflow/modules/als_top/
WORKDIR /opt/airflow

COPY requirements.txt entrypoint_airflow.sh ./
COPY --chown=airflow:root ./dags /opt/airflow/dags

RUN pip install --no-index --find-links=/opt/wheels -r requirements.txt
