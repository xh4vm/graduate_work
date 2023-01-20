FROM python:3.10-slim AS producer-storage-builder

WORKDIR /opt
COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends gcc musl-dev libc-dev librdkafka-dev && \
     pip install --upgrade pip \
     && pip install wheel && pip3 wheel -r requirements.txt --wheel-dir=/opt/wheels


FROM python:3.10-slim

COPY --from=producer-storage-builder /opt /opt
COPY --from=producer-storage-builder /usr/lib/ /usr/lib/
ENV PYTHONPATH "/opt/content/modules/auth/src/:/opt/content/modules/auth/src:/opt/content/modules/auth/src/messages"

WORKDIR /opt/content
ENTRYPOINT ["/bin/bash", "-c", "chmod +x ./start.sh && ./start.sh"]

COPY . .
RUN pip install --no-index --find-links=/opt/wheels -r requirements.txt