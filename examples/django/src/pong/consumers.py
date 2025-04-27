from config.ecore import ecore

from eventscore.core.types import Event


@ecore.consumer(event="ping", group="medium1", clones=2)
def pong1(event: Event) -> None:
    print("Django pong #1: ", event)


@ecore.consumer(event="ping", group="medium2", clones=1)
def pong2(event: Event) -> None:
    print("Django pong #2: ", event)
