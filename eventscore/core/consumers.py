from typing import Awaitable, Any, Callable

from eventscore.core.abstract import IASyncConsumer, IConsumer
from eventscore.core.events import Event


class AsyncConsumer(IASyncConsumer):
    def __init__(self, func: Callable[[Event], Awaitable[Any]]) -> None:
        self.__func = func

    async def consume(self, event: Event) -> None:
        await self.__func(event)


class Consumer(IConsumer):
    def __init__(self, func: Callable[[Event], Any]) -> None:
        self.__func = func

    def consume(self, event: Event) -> None:
        self.__func(event)
