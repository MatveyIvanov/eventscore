import logging

from eventscore.core.abstract import IECore, IProducer
from eventscore.core.logging import logger as _logger
from eventscore.core.types import Event


class Producer(IProducer):
    def __init__(self, ecore: IECore, logger: logging.Logger = _logger) -> None:
        """
        Construct producer instance

        :param ecore: Event core instance
        :type ecore: IECore
        """
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
        self.__logger.info(f"Successfully produced an event: {event}.")
