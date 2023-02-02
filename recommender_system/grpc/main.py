import asyncio
import logging

from core.config import CONFIG, logger
from grpc import aio
from grpc._compression import Gzip
from messages.recommendation_pb2_grpc import add_RecommenderServicer_to_server
from services.grpc.recommendation import RecommenderServer
from services.storage.mongo import BaseDB, AsyncMongoDB


async def serve(db: BaseDB, logger: logging.Logger):
    server = aio.server(
        options=(
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
        ),
        compression=Gzip,
    )
    add_RecommenderServicer_to_server(RecommenderServer(db), server)

    server.add_insecure_port(f'{CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}')

    logger.info(f'GRPC server running on {CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}.')

    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    db = AsyncMongoDB(settings=CONFIG.DB)
    asyncio.run(serve(db=db, logger=logger))
