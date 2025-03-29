from config.ecore import ecore
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eventscore.core.types import Event


class PingViewSet(GenericViewSet):
    @action(detail=False, methods=["GET"])
    def ping(self, request):
        ecore.produce(event=Event(type="ping", payload={"some": "value"}))
        return Response(data={"detail": "OK"})
