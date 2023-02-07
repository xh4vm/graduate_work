import asyncio
import logging

from core.config import CONFIG, logger
from grpc import aio
from grpc._compression import Gzip
from messages.recommendation_pb2_grpc import add_RecommenderServicer_to_server
from services.grpc.recommender import RecommenderServer
from services.storage.mongo import AsyncMongoDB
from services.cache.redis import RedisCache
from services.recommender import RecommenderService


async def serve(recommender_service: RecommenderService, logger: logging.Logger):
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
    add_RecommenderServicer_to_server(RecommenderServer(recommender_service), server)

    server.add_insecure_port(f'{CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}')

    logger.info(f'GRPC server running on {CONFIG.GRPC.HOST}:{CONFIG.GRPC.PORT}.')

    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    db = AsyncMongoDB(settings=CONFIG.DB)
    cache = RedisCache(settings=CONFIG.CACHE)
    recommender_service = RecommenderService(cache=cache, db=db)
    
    asyncio.run(serve(recommender_service=recommender_service, logger=logger))
