FROM openkbs/jre-mvn-py3:v1.3.1

RUN pip install jupyter pyspark==3.0.1

CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
