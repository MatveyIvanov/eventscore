import time

from config.ecore import ecore

from eventscore.core.logging import logger
from eventscore.core.types import Event


@ecore.consumer(
    event="payment-init",
    group="payment-init",
)
def payment_init(event: Event):
    time.sleep(1)  # Some external payment system API call
    logger.info(f"Payment initialized for event: {event}")
