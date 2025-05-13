import random
from decimal import Decimal

from config.di import Container
from dependency_injector.wiring import Provide, inject

from eventscore.core.abstract import IECore
from eventscore.core.types import Event
from eventscore.decorators import consumer


@consumer(
    ecore=Container.ecore(),
    event="product-purchase",
    group="product-purchase",
)
@inject
def product_purchase(event: Event, ecore: IECore = Provide[Container.ecore]):
    in_stock = random.random() < 0.75
    if in_stock:
        ecore.produce(
            Event(
                type="payment-init",
                payload={**event.payload, "amount": Decimal("100")},
            )
        )
    else:
        ecore.produce(Event(type="product-out-of-stock", payload=event.payload))
