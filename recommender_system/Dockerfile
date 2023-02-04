FROM python:3.6-slim

WORKDIR /opt/content
ENV PYTHONPATH "/opt/content/:/opt/content/src"

COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends openjdk-11-jdk && \
     pip install --upgrade pip \
     && pip install wheel && pip3 wheel -r requirements.txt --wheel-dir=/opt/wheels

ENTRYPOINT [ "/bin/bash", "-c",  "celery --app=recommender_tasks worker --loglevel=info & celery --app=recommender_tasks beat --loglevel=info -f /opt/content/log/celery_beat.log" ]

COPY . .

RUN pip install --no-index --find-links=/opt/wheels -r requirements.txt
