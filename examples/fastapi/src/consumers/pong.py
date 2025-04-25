from eventscore.core.types import Event

from config.ecore import ecore


@ecore.consumer(event="ping", group="medium", clones=1)
def pong(event: Event) -> None:
    print(event)

