from eventscore.core.types import Event
from examples.django.src.config.ecore import ecore


@ecore.consumer(event="ping", group="medium", clones=1)
def pong(event: Event) -> None:
    print(event)
