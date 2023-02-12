from core.config import CONFIG, logger
from services.storage.base import BaseDB
from services.cache.base import BaseCache
from models.user import User
from models.recommendation import Recommendation


class RecommenderService:
    def __init__(self, cache: BaseCache, db: BaseDB) -> None:
        self._db = db
        self._cache = cache

    async def get_recommendations(self, user: User, save_cache: bool = False) -> Recommendation:
        logger.info('Checking cache into for user "%s"', user.id_str)
        recomendation: Recommendation | None = await self._cache.get(key=f'recommendation::{user.id_str}')
        
        if recomendation is not None:
            return Recommendation(**recomendation)

        logger.info('Looking database for user "%s"', user.id_str)
        raw_document = await self._db.last_one(
            db_name=CONFIG.DB.DB_NAME,
            collection_name=CONFIG.DB.COLLECTION_NAME,
            filter={'user_id': user.id},
            sorts=[('_id', -1)]
        )
        logger.info('Success searching recommendations for user "%s"', user.id_str)

        if raw_document is None:
            logger.info('Nothing found for user "%s"', user.id_str)
            return Recommendation(user_id=user.id)

        logger.info('Transforming data for user "%s"', user.id_str)
        recomendation = Recommendation(**raw_document)

        if save_cache:
            logger.info('Saving data for user "%s"', user.id_str)
            await self._cache.set(key=f'recommendation::{user.id_str}', data=recomendation.dict())
        
        return recomendation
