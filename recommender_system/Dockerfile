FROM openkbs/jre-mvn-py3:v1.3.1

WORKDIR /opt/content
COPY requirements.txt ./

RUN apt-get update && pip install --upgrade pip \
     && pip install wheel && pip3 wheel -r requirements.txt --wheel-dir=/opt/wheels

COPY . .

CMD []
