from config.ecore import ecore
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eventscore.core.types import Event


class PingViewSet(GenericViewSet):
    @action(detail=False, methods=["POST"])
    def ping(self, request: Request):
        event_type, payload = request.data.get("event"), request.data.get("payload")
        ecore.produce(event=Event(type=event_type, payload=payload))
        return Response(data={"detail": "OK"})
