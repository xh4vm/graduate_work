import jwt
from core.config import CONFIG, grpc_logger
from messages.recommendation_pb2 import RecommendationResponse
from messages.recommendation_pb2_grpc import RecommenderServicer


class RecommenderServer(RecommenderServicer):
    async def get_recomendations(self, request, context):
        pass
