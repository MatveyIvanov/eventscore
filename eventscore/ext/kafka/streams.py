from typing import Any, TypeAlias

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaTimeoutError

from eventscore.core.abstract import EventType, IEventSerializer, IStream
from eventscore.core.exceptions import (
    EmptyStreamError,
    EventNotSentError,
    TooManyDataError,
)
from eventscore.core.types import Event

PollResult: TypeAlias = dict[str, list[dict[str, Any]]]


class KafkaStream(IStream):
    def __init__(
        self,
        serializer: IEventSerializer[dict, bytes],
    ) -> None:
        self.__serializer = serializer
        configs = {}
        self.__producer = KafkaProducer(**configs)
        self.__consumer = KafkaConsumer(**configs)
        self.__consumer_subscription: EventType | None = None

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        record = self.__producer.send(
            topic=str(event),
            value=self.__serializer.encode(event),
        )
        if not block:
            return

        try:
            record.get(timeout)
        except KafkaTimeoutError as exc:
            raise EventNotSentError from exc

    def pop(
        self,
        event: EventType,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        self.__single_consumer_subscription_lock(event)
        record: PollResult = self.__consumer.poll(
            timeout * 1000 if block else 0,
            max_records=1,
            update_offsets=True,
        )
        if event not in record or not record[event]:
            raise EmptyStreamError
        if len(record[event]) > 1:
            raise TooManyDataError

        data = record[event][0]
        return self.__serializer.decode(data)

    def __single_consumer_subscription_lock(self, event: EventType) -> None:
        if self.__consumer_subscription == event:
            return
        if self.__consumer_subscription is not None:
            self.__consumer.unsubscribe()

        self.__consumer_subscription = event
        self.__consumer.subscribe(topics=[str(event)])
