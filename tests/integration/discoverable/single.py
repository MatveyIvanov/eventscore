from eventscore.core.types import Event
from eventscore.decorators import consumer
from tests.integration.discoverable import ecore


@ecore.consumer(event="event", group="group")
def consumer_ecore(event: Event):
    pass


@consumer(ecore=ecore, event="event", group="group")
def consumer(event: Event):
    pass
