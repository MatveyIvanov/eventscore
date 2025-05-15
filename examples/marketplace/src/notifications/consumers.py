import time

from config.ecore import ecore

from eventscore.core.logging import logger
from eventscore.core.types import Event


@ecore.consumer(
    event="product-out-of-stock",
    group="product-out-of-stock",
)
def payment_init(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Product out of stock notification sent for event: {event}")


@ecore.consumer(
    event="payment-completed",
    group="payment-completed",
)
def payment_completed(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Payment success notification sent for event: {event}")


@ecore.consumer(
    event="payment-failed",
    group="payment-failed",
)
def payment_failed(event: Event):
    time.sleep(1)  # Some external notification system API call
    logger.info(f"Payment failure notification sent for event: {event}")
