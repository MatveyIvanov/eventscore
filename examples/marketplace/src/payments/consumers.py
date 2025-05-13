import time

from config.di import Container

from eventscore.core.logging import logger
from eventscore.core.types import Event
from eventscore.decorators import consumer


@consumer(
    ecore=Container.ecore(),
    event="payment-init",
    group="payment-init",
)
def payment_init(event: Event):
    time.sleep(1)  # Some external payment system API call
    logger.info(f"Payment initialized for event: {event}")
