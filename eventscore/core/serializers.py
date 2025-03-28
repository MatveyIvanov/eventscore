import json
from dataclasses import asdict

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event


class EventSerializer(IEventSerializer):
    def encode(self, event: Event) -> bytes:
        return json.dumps(asdict(event)).encode()

    def decode(self, event: bytes) -> Event:
        return Event(**json.loads(event.decode()))
