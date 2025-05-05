from eventscore.core.types import Event
from tests.integration.discoverable import ecore


@ecore.consumer(event="event1", group="multiple-group1")
def consumer1(event: Event):
    pass


@ecore.consumer(event="event2", group="multiple-group1")
def consumer2(event: Event):
    pass
