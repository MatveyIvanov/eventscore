import random

from config.di import Container
from dependency_injector.wiring import Provide, inject
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eventscore.core.abstract import IECore
from eventscore.core.types import Event


class PaymentViewSet(GenericViewSet):
    @action(methods=["POST"])
    @inject
    def webhook(
        self,
        request,
        ecore: IECore = Provide[Container.ecore],
        *args,
        **kwargs,
    ):
        success = random.random() < 0.75
        if success:
            ecore.produce(
                Event(
                    type="payment-completed",
                    payload={"product_id": request.data["product_id"]},
                ),
                block=True,
            )
        else:
            ecore.produce(
                Event(
                    type="payment-failed",
                    payload={"product_id": request.data["product_id"]},
                ),
                block=True,
            )

        return Response("OK")
