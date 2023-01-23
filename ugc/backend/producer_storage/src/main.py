from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware import Middleware
from starlette_context import plugins
from dependency_injector import providers
from starlette_context.middleware import RawContextMiddleware

from .resources.json_serializer import JSONSerializerResource
from .resources.string_serializer import StringSerializerResource

from .containers.movie import ServiceContainer as MovieFrameServiceContainer

from .api.v1.movies import router as movie_router
from .core.config import CONFIG


def register_di_containers():
    movie_frame_value_serializer = providers.Resource(
        JSONSerializerResource,
        to_dict=lambda obj: obj.dict(),
    )
    movie_frame_key_serializer = providers.Resource(StringSerializerResource, codec='utf-8')

    MovieFrameServiceContainer(
        key_serializer=movie_frame_key_serializer, value_serializer=movie_frame_value_serializer
    )


def register_routers(app: FastAPI):
    API_PATH = f'{CONFIG.APP.API_PATH}/{CONFIG.APP.API_VERSION}'

    app.include_router(router=movie_router, prefix=API_PATH)


def create_app():
    middleware = [Middleware(RawContextMiddleware, plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()))]

    app = FastAPI(
        title=CONFIG.APP.PROJECT_NAME,
        docs_url=f'{CONFIG.APP.API_PATH}{CONFIG.APP.SWAGGER_PATH}',
        openapi_url=f'{CONFIG.APP.API_PATH}{CONFIG.APP.JSON_SWAGGER_PATH}',
        default_response_class=ORJSONResponse,
        middleware=middleware,
    )

    register_routers(app=app)
    register_di_containers()

    return app


app = create_app()
