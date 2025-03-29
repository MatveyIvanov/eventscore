import threading

from eventscore.core.abstract import EventType, IConsumer, IRunner, IStream
from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.logging import logger


class ObserverRunner(IRunner):
    def __init__(
        self,
        stream: IStream,
        event: EventType,
        *consumers: IConsumer,
    ) -> None:
        self.__stream = stream
        self.__event = event
        self.__consumers = consumers
        self.__logger = logger

    def run(self) -> None:
        while True:
            try:
                event = self.__stream.pop(self.__event, block=True)
            except EmptyStreamError:
                self.__logger.debug("Stream is empty, no consumers ran this iteration.")
                continue

            tasks = [
                threading.Thread(target=consumer.consume, args=(event,))
                for consumer in self.__consumers
            ]
            for task in tasks:
                task.start()
                self.__logger.debug(f"Consumer thread {task.ident} has started.")

            for task in tasks:
                task.join()
                self.__logger.debug(f"Consumer thread {task.ident} has finished.")
