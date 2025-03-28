from eventscore.core.abstract import ConsumerFunc, IConsumer
from eventscore.core.types import Event


class Consumer(IConsumer):
    def __init__(self, func: ConsumerFunc) -> None:
        self.__func = func

    def consume(self, event: Event) -> None:
        self.__func(event)
