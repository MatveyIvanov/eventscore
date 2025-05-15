import logging

from eventscore.core.abstract import ConsumerFunc, IConsumer
from eventscore.core.logging import logger as _logger
from eventscore.core.types import Event


class Consumer(IConsumer):
    def __init__(self, func: ConsumerFunc, logger: logging.Logger = _logger) -> None:
        self.__func = func
        self.__logger = logger

    def consume(self, event: Event) -> None:
        self.__logger.debug("Consumer started.")
        self.__func(event)
        self.__logger.info(
            f"[{self.__func.__name__}] " + f"Successfully consumed an event: {event}."
        )
