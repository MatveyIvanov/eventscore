from eventscore.core.abstract import ConsumerFunc, IConsumer
from eventscore.core.logging import logger
from eventscore.core.types import Event


class Consumer(IConsumer):
    def __init__(self, func: ConsumerFunc) -> None:
        self.__func = func
        self.__logger = logger

    def consume(self, event: Event) -> None:
        self.__logger.debug("Consumer started.")
        self.__func(event)
        self.__logger.debug("Consumer finished.")
