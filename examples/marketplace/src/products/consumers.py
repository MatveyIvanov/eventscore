import random
from decimal import Decimal

from config.ecore import ecore

from eventscore.core.types import Event


@ecore.consumer(
    event="product-purchase",
    group="product-purchase",
)
def product_purchase(event: Event):
    in_stock = random.random() < 0.75
    if in_stock:
        ecore.produce(
            Event(
                type="payment-init",
                payload={**event.payload, "amount": str(Decimal("100"))},
            )
        )
    else:
        ecore.produce(Event(type="product-out-of-stock", payload=event.payload))
