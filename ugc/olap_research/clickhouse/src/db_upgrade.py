from adapters.clickhouse.client import ClickHouseClient, ClickHouseMigrator
from services import DBService
from settings import ch_settings

node_prefix = ch_settings.CH_NODE_PREFIX
node_ports = ch_settings.CH_NODE_PORTS
local_mode = ch_settings.CH_LOCAL_MODE
db_name = ch_settings.CH_DB_NAME
replica_name = ch_settings.CH_REPLICA_DB_NAME

db_service = DBService()
for i in range(ch_settings.CH_NODE_NUM):
    db_client = ClickHouseClient(
        host="localhost" if local_mode else f"{node_prefix}{i + 1}",
        port=node_ports[i] if local_mode else None,
    )
    db_service.db_migrators.append(
        ClickHouseMigrator(
            client=db_client,
            db_name=db_name if i % 2 == 0 else replica_name,
            cluster_name=ch_settings.CH_CLUSTER_NAME,
        )
    )

if __name__ == "__main__":
    db_service.db_upgrade()
