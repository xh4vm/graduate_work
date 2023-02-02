from core.config import CONFIG, logger
from messages.recommendation_pb2 import RecommendationResponse
from messages.recommendation_pb2_grpc import RecommenderServicer
from services.storage.base import BaseDB
from models.user import User
from models.recommendation import Recommendation


class RecommenderServer(RecommenderServicer):
    def __init__(self, db: BaseDB) -> None:
        self.db = db

    async def get_recommendations(self, request, context):
        user = User(id=request.user_id)

        logger.info('Looking for recommendations for user "%s"', user.id_str)
        raw_document = await self.db.one(
            db_name=CONFIG.DB.DB_NAME,
            collection_name=CONFIG.DB.DB_NAME,
            filter={'user_id': user.id_str}
        )
        logger.info('Success searching recommendations for user "%s"', user.id_str)

        if raw_document is None:
            logger.info('Nothing found for user "%s"', user.id_str)
            return RecommendationResponse(user_id=user.id_str, movies_id=[])

        document = Recommendation(**raw_document)

        logger.info('Transforming data for user "%s"', user.id_str)
        return RecommendationResponse(**document.dict())
