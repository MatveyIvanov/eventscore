from eventscore.core.abstract import IECore, IProducer
from eventscore.core.types import Event
from eventscore.core.logging import logger


class Producer(IProducer):
    def __init__(self, ecore: IECore) -> None:
        self.__ecore = ecore
        self.__logger = logger

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        self.__logger.debug(
            f"Producing event {event} with block={block}, timeout={timeout}."
        )
        self.__ecore.stream.put(event=event, block=block, timeout=timeout)
        self.__logger.debug(f"Event {event.uid} produced.")
