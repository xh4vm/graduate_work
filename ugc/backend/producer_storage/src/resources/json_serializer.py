import json
from typing import Callable, Any
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from pydantic.main import ModelMetaclass

from dependency_injector import resources


class JSONSerializerResource(resources.Resource):
    def init(
        self,
        schema: dict[str, Any],
        registry: SchemaRegistryClient,
        to_dict: Callable[[ModelMetaclass], dict[str, Any]] = None,
    ) -> JSONSerializer:
        return JSONSerializer(schema_str=json.dumps(schema), schema_registry_client=registry, to_dict=to_dict)
