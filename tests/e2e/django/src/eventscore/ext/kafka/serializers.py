import json

from eventscore.core.abstract import IEventSerializer
from eventscore.core.types import Event, EventDict


class KafkaEventSerializer(IEventSerializer[EventDict, bytes]):
    def encode(self, event: Event) -> bytes:
        return json.dumps(event.asdict()).encode()

    def decode(self, event: EventDict) -> Event:
        return Event.fromdict(event)
