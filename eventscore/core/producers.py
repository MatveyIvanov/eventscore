from eventscore.core.abstract import IECore, IProducer
from eventscore.core.types import Event


class Producer(IProducer):
    def __init__(self, ecore: IECore) -> None:
        self.__ecore = ecore

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        self.__ecore.stream.put(event=event, block=block, timeout=timeout)
