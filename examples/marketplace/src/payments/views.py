import random

from config.ecore import ecore
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eventscore.core.types import Event


class PaymentViewSet(GenericViewSet):
    @action(methods=["POST"], detail=False)
    def webhook(
        self,
        request,
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
