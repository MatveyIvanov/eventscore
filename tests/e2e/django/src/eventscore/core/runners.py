import logging
import threading

from eventscore.core.abstract import (
    ConsumerGroup,
    EventType,
    IConsumer,
    IRunner,
    IStreamFactory,
)
from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.logging import logger as _logger


class ObserverRunner(IRunner):
    def __init__(
        self,
        stream_factory: IStreamFactory,
        event: EventType,
        group: ConsumerGroup,
        *consumers: IConsumer,
        max_events: int = -1,
        logger: logging.Logger = _logger,
    ) -> None:
        self.__stream = stream_factory()
        self.__event = event
        self.__group = group
        self.__max_events = max_events
        self.__consumers = consumers
        self.__logger = logger

        assert len(consumers) > 0, "No consumers provided to runner."
        assert max_events == -1 or max_events > 0, "Max events must be positive or -1."

    def run(self) -> None:
        events_counter = 0
        while self.__max_events == -1 or events_counter < self.__max_events:
            try:
                event = self.__stream.pop(self.__event, self.__group, block=True)
            except EmptyStreamError:
                self.__logger.debug("Stream is empty, no consumers ran this iteration.")
                continue

            events_counter += 1
            tasks = tuple(
                threading.Thread(target=consumer.consume, args=(event,))
                for consumer in self.__consumers
            )
            for task in tasks:
                task.start()
                self.__logger.debug(f"Consumer thread {task.ident} has started.")

            for task in tasks:
                task.join()
                self.__logger.debug(f"Consumer thread {task.ident} has finished.")
