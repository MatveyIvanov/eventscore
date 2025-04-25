import json

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event


class KafkaEventSerializer(IEventSerializer[dict, bytes]):
    def encode(self, event: Event) -> bytes:
        return json.dumps(event.asdict()).encode()

    def decode(self, event: dict) -> Event:
        return Event.fromdict(event)
