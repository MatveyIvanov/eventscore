from config.ecore import ecore

from eventscore.core.types import Event


@ecore.consumer(event="ping", group="medium", clones=1)
def pong(event: Event) -> None:
    print("FastAPI ponged: ", event)
