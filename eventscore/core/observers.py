import asyncio
import threading

from eventscore.core.abstract import IASyncConsumer, IConsumer, IObserver, IStream
from eventscore.core.events import TEvent


class Observer(IObserver):
    def __init__(
        self,
        stream: IStream,
        event: TEvent,
        *consumers: IConsumer | IASyncConsumer,
    ) -> None:
        self.__stream = stream
        self.__event = event
        self.__consumers = consumers

    def run(self) -> None:
        pass

    def __listener(self) -> None:
        while True:
            event = self.__stream.pop(self.__event, block=True)

            tasks = [
                threading.Thread(target=consumer.consume, args=(event,))
                for consumer in self.__consumers
            ]
            for task in tasks:
                task.start()

    async def __alistener(self) -> None:
        while True:
            event = await self.__stream.pop(self.__event, block=True)
            tasks = [
                asyncio.Task(consumer.consume(event)) for consumer in self.__consumers
            ]
            await asyncio.gather(*tasks)
