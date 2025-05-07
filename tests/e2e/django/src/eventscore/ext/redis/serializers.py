import json

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event


class RedisEventSerializer(IEventSerializer[bytes, str]):
    def encode(self, event: Event) -> str:
        return json.dumps(event.asdict())

    def decode(self, event: bytes) -> Event:
        return Event.fromdict(json.loads(event.decode()))
