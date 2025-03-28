import json
from dataclasses import asdict
from typing import Dict

from redis.typing import EncodableT, FieldT

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event


class RedisEventSerializer(IEventSerializer[bytes, Dict[FieldT, EncodableT]]):
    def encode(self, event: Event) -> Dict[FieldT, EncodableT]:
        return asdict(event)

    def decode(self, event: bytes) -> Event:
        return Event(**json.loads(event.decode()))
