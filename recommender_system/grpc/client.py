from grpc import aio
from messages.recommendation_pb2 import RecommendationRequest, RecommendationResponse
from messages.recommendation_pb2_grpc import RecommenderStub


class PermissionClient:
    def __init__(self, channel: aio.Channel) -> None:
        self.client = RecommenderStub(channel)

    async def get_recommendations(self, user_id: str) -> RecommendationResponse:
        request = RecommendationRequest(user_id=user_id)
        response = await self.client.get_recommendations(request)

        return {'user_id': response.user_id, 'movies_id': response.movies_id}
