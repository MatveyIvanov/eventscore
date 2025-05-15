import time

from config.ecore import ecore

from eventscore.core.logging import logger
from eventscore.core.types import Event


@ecore.consumer(
    event="payment-completed",
    group="payment-completed",
)
def payment_completed(event: Event):
    time.sleep(0.1)  # Some DB call for stats update
    logger.info(f"Payment success stat updated for event: {event}")
