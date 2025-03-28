import threading

from eventscore.core.abstract import EventType, IConsumer, IRunner, IStream


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

    def run(self) -> None:
        while True:
            event = self.__stream.pop(self.__event, block=True)

            tasks = [
                threading.Thread(target=consumer.consume, args=(event,))
                for consumer in self.__consumers
            ]
            for task in tasks:
                task.start()

            for task in tasks:
                task.join()
