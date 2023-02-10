FROM python:3.10-slim

WORKDIR /opt/content
ENV PYTHONPATH "/opt/content/:/opt/content/src"

COPY ./mongodb_initer/requirements.txt ./

RUN apt-get update && pip install --upgrade pip && pip install wheel && pip3 wheel -r requirements.txt --wheel-dir=/opt/wheels


ENTRYPOINT ["/bin/bash", "-c", "chmod +x ./init_mongodb.sh && ./init_mongodb.sh"]

COPY ./.env ./
COPY ./mongodb_initer/init_mongodb.sh ./
COPY ./mongodb_initer/src ./src

RUN pip install --no-index --find-links=/opt/wheels -r requirements.txt
