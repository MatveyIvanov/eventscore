import time

from config.di import Container

from eventscore.core.logging import logger
from eventscore.core.types import Event
from eventscore.decorators import consumer


@consumer(
    ecore=Container.ecore(),
    event="product-out-of-stock",
    group="product-out-of-stock",
)
def payment_init(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Product out of stock notification sent for event: {event}")


@consumer(
    ecore=Container.ecore(),
    event="payment-completed",
    group="payment-completed",
)
def payment_completed(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Payment success notification sent for event: {event}")


@consumer(
    ecore=Container.ecore(),
    event="payment-falied",
    group="payment-falied",
)
def payment_failed(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Payment failure notification sent for event: {event}")
