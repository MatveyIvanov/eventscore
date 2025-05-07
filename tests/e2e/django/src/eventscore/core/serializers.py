import json

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event


class EventSerializer(IEventSerializer[bytes, bytes]):
    def encode(self, event: Event) -> bytes:
        return json.dumps(event.asdict()).encode()

    def decode(self, event: bytes) -> Event:
        return Event.fromdict(json.loads(event.decode()))
