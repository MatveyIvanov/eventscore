import json
from datetime import UTC, datetime

from config.ecore import ecore
from events.models import EventLog, EventModel

from eventscore.core.types import Event


@ecore.consumer(event="ping", group="loggers", clones=1)
def pong_logger(event: Event) -> None:
    EventLog.objects.create(
        data=repr(event),
        dt=datetime.fromtimestamp(float(event.ts), tz=UTC),
    )


@ecore.consumer(event="ping", group="handlers", clones=3)
def pong_handler(event: Event) -> None:
    EventModel.objects.get_or_create(
        uid=event.uid,
        defaults={
            "type": event.type,
            "ts": event.ts,
            "payload": json.dumps(event.payload),
        },
    )
