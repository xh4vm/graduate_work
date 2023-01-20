import json
from typing import Callable, Any
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from pydantic.main import ModelMetaclass

from dependency_injector import resources


class AvroSerializerResource(resources.Resource):
    def init(
        self,
        schema: dict[str, Any],
        registry: SchemaRegistryClient,
        to_dict: Callable[[ModelMetaclass], dict[str, Any]] = None,
    ) -> AvroSerializer:
        return AvroSerializer(schema_str=json.dumps(schema), schema_registry_client=registry, to_dict=to_dict)
