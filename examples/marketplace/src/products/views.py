from config.di import Container
from dependency_injector.wiring import Provide, inject
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from eventscore.core.abstract import IECore
from eventscore.core.types import Event


class ProductViewSet(GenericViewSet, mixins.RetrieveModelMixin):
    def get_queryset(self):
        return [{"id": 1, "name": 1}]

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg not in self.kwargs:
            return None
        filtered = filter(
            lambda product: product["id"] == self.kwargs[lookup_url_kwarg],
            self.get_queryset(),
        )
        try:
            return next(filtered)
        except StopIteration:
            return None

    @action(methods=["POST"], detail=True)
    @inject
    def purchase(
        self,
        request,
        ecore: IECore = Provide[Container.ecore],
        *args,
        **kwargs,
    ):
        product = self.get_object()
        if not product:
            return Response(status=404)

        ecore.produce(
            Event(
                type="product-purchase",
                payload={"product": product, "user": request.user.__repr__()},
            ),
            block=True,
        )

        return Response()
