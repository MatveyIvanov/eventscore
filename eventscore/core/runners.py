import threading

from eventscore.core.abstract import EventType, IConsumer, IRunner, IStream
from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.logging import logger


class ObserverRunner(IRunner):
    def __init__(
        self,
        stream: IStream,
        event: EventType,
        max_events: int = -1,
        *consumers: IConsumer,
    ) -> None:
        self.__stream = stream
        self.__event = event
        self.__max_events = max_events
        self.__consumers = consumers
        self.__logger = logger

        assert len(consumers) > 0, "No consumers provided to runner."
        assert max_events == -1 or max_events > 0, "Max events must be positive."

    def run(self) -> None:
        events_counter = 0
        while self.__max_events == -1 or events_counter < self.__max_events:
            try:
                event = self.__stream.pop(self.__event, block=True)
            except EmptyStreamError:
                self.__logger.debug("Stream is empty, no consumers ran this iteration.")
                continue

            events_counter += 1
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
