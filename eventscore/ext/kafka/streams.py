from typing import Any, TypeAlias

from kafka import KafkaConsumer, KafkaProducer  # type:ignore[import-untyped]
from kafka.errors import KafkaTimeoutError  # type:ignore[import-untyped]
from kafka.producer.future import FutureRecordMetadata  # type:ignore[import-untyped]

from eventscore.core.abstract import ConsumerGroup, EventType, IEventSerializer, IStream
from eventscore.core.exceptions import (
    EmptyStreamError,
    EventNotSentError,
    TooManyDataError,
)
from eventscore.core.types import Event, EventDict

PollResult: TypeAlias = dict[str, list[EventDict]]


class KafkaStream(IStream):
    def __init__(
        self,
        serializer: IEventSerializer[EventDict, bytes],
    ) -> None:
        self.__serializer = serializer
        configs: dict[str, Any] = {}
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
        record: FutureRecordMetadata = (  # type:ignore
            self.__producer.send(  # pyright:ignore[reportUnknownMemberType]
                topic=str(event),
                value=self.__serializer.encode(event),
            )
        )
        if not block:
            return

        try:
            _ = record.get(  # pyright:ignore[reportUnknownMemberType,reportUnknownVariableType]  # noqa:E501
                timeout
            )
        except KafkaTimeoutError as exc:
            raise EventNotSentError from exc

    def pop(
        self,
        event: EventType,
        group: ConsumerGroup,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        self.__single_consumer_subscription_lock(event)
        record: PollResult = (  # pyright:ignore[reportUnknownVariableType]
            self.__consumer.poll(  # pyright:ignore[reportUnknownMemberType]
                timeout * 1000 if block else 0,
                max_records=1,
                update_offsets=True,
            )
        )
        if event not in record or not record[str(event)]:
            raise EmptyStreamError
        if len(record[str(event)]) > 1:
            raise TooManyDataError

        data = record[str(event)][0]
        return self.__serializer.decode(data)

    def __single_consumer_subscription_lock(self, event: EventType) -> None:
        if self.__consumer_subscription == event:
            return
        if self.__consumer_subscription is not None:
            self.__consumer.unsubscribe()

        self.__consumer_subscription = event
        self.__consumer.subscribe(  # pyright:ignore[reportUnknownMemberType]
            topics=[str(event)]
        )
