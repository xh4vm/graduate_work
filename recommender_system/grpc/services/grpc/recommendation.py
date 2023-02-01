from core.config import CONFIG, grpc_logger
from messages.recommendation_pb2 import RecommendationResponse
from messages.recommendation_pb2_grpc import RecommenderServicer
from services.storage.base import BaseDB


class RecommenderServer(RecommenderServicer):
    def __init__(self, db: BaseDB) -> None:
        self.db = db

    async def get_recommendations(self, request, context):
        return RecommendationResponse(user_id='0', movies_id=['1', '2', '3'])
