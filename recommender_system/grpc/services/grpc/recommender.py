import uuid
from core.config import logger
from messages.recommendation_pb2 import RecommendationResponse
from messages.recommendation_pb2_grpc import RecommenderServicer
from models.user import User
from models.recommendation import Recommendation
from services.recommender import RecommenderService


class RecommenderServer(RecommenderServicer):
    def __init__(self, recommender: RecommenderService) -> None:
        self._recommender = recommender

    async def get_recommendations(self, request, context):
        user = User(id=request.user_id)

        recommendation: Recommendation = await self._recommender.get_recommendations(user=user)

        if recommendation.movies_id == []:
            logger.info('It is anonymous user')
            anonymous_user = User(id=uuid.UUID(int=0))
            recommendation: Recommendation = await self._recommender.get_recommendations(user=anonymous_user, save_cache=True)

        return RecommendationResponse(**recommendation.serializable_dict())
