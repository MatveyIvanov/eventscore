import time

from config.di import Container

from eventscore.core.logging import logger
from eventscore.core.types import Event
from eventscore.decorators import consumer


@consumer(
    ecore=Container.ecore(),
    event="payment-completed",
    group="payment-completed",
)
def payment_completed(event: Event):
    time.sleep(0.1)  # Some DB call for stats update
    logger.info(f"Payment success stat updated for event: {event}")
