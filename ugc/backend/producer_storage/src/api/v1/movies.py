from modules.auth.src.payloads.fastapi import UserAccessRequired

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Body

from src.containers.movie import ServiceContainer
from src.services.producer.kafka import KafkaProducer
from src.core.config import CONFIG
from src.utils.error_handlers.auth import error_handler

from src.models.movie import MovieFrameDatagram, MovieFrame


router = APIRouter(prefix='/movie', tags=['Movies'])
URL = f'{CONFIG.APP.HOST}:{CONFIG.APP.PORT}{CONFIG.APP.API_PATH}/{CONFIG.APP.API_VERSION}/movie/frame'


@router.post(path='/frame', name='Produce storage user data')
@inject
def movie_frame(
    _error_handler: None = Depends(error_handler),
    frame: MovieFrameDatagram = Body(title='MovieFrame', alias='movie_frame'),
    user_id: str = Depends(UserAccessRequired(permissions={URL: 'POST'})),
    kafka_producer: KafkaProducer = Depends(Provide[ServiceContainer.kafka_producer]),
) -> None:

    user_frame = MovieFrame(**frame.dict())
    kafka_producer.produce(topic=CONFIG.KAFKA.TOPICS.MOVIE_FRAME, key=user_id, value=user_frame)
