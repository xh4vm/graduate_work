import json


def get_data_from_json(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return (data)


def quiet_logs(sc):
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
    logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )
