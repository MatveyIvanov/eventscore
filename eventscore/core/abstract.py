from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum, StrEnum
from typing import Any, Protocol, TypeAlias, TypeVar

from eventscore.core.types import Event, Pipeline, Worker

EventType: TypeAlias = str | StrEnum | IntEnum
ConsumerFunc: TypeAlias = Callable[[Event], Any]
ConsumerGroup: TypeAlias = str | StrEnum | IntEnum

IType = TypeVar("IType", contravariant=True)
RType = TypeVar("RType", covariant=True)


class IECore(Protocol):
    __slots__ = ()

    @property
    def process_pipeline(self) -> IProcessPipeline:
        """
        Pipeline processor getter

        :return: Pipeline processor
        :rtype: IProcessPipeline
        """
        ...

    @property
    def spawn_worker(self) -> ISpawnWorker:
        """
        Worker spawner getter

        :return: Worker spawner
        :rtype: ISpawnWorker
        """
        ...

    @property
    def producer(self) -> IProducer:
        """
        Producer getter

        :return: Producer
        :rtype: IProducer
        """
        ...

    @property
    def stream(self) -> IStream:
        """
        Stream getter

        :return: Stream
        :rtype: IStream
        """
        ...

    def consumer(
        self,
        func: ConsumerFunc | None = None,
        *,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> ConsumerFunc:
        """
        Decorator for consumer functions

        :param func: function to decorate
        :type func: ConsumerFunc | None
        :param event: Event type
        :type event: EventType
        :param group: Consumer group
        :type group: ConsumerGroup
        :param clones: No of clones
        :type clones: int
        :return: Decorated function
        :rtype: ConsumerFunc
        """
        ...

    def register_consumer(
        self,
        func: ConsumerFunc,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> None:
        """
        Consumer function registrator

        :param func: Function to register as a consumer
        :type func: ConsumerFunc
        :param event: Event type
        :type event: EventType
        :param group: Consumer group
        :type group: ConsumerGroup
        :param clones: No of clones
        :type clones: int
        :return: None
        :rtype: None
        """
        ...

    def discover_consumers(self, *, root: str | None = None) -> None:
        """

        :param root: root package to search in.
            Current directory is used by default.
        :type root: str | None
        :return: None
        :rtype: None
        """
        ...

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        """
        Produce an event

        :param event: Event to produce
        :type event: Event
        :param block: Should I/O be blocked if some delay occurs.
            Defaults to `True`.
        :type block: bool
        :param timeout: Number of seconds to wait in case of latency.
            Defaults to `5`.
        :type timeout: int
        :return: None
        :rtype: None
        """
        ...

    def spawn_workers(self) -> None:
        """
        Spawn workers for registered consumers.
        Further consumer registering and spawning won't matter

        :return: None
        :rtype: None
        """
        ...


class IProcessPipeline(Protocol):
    __slots__ = ()

    def __call__(self, pipeline: Pipeline, ecore: IECore) -> Worker:
        """
        Process a pipeline

        :param pipeline: Pipeline to process
        :type pipeline: Pipeline
        :param ecore: Event core instance
        :type ecore: IECore
        :return: Constructed worker
        :rtype: Worker
        """
        ...


class ISpawnWorker(Protocol):
    __slots__ = ()

    def __call__(self, worker: Worker) -> None:
        """
        Spawn worker

        :param worker: Worker to spawn
        :type worker: Worker
        :return: None
        :rtype: None
        """
        ...


class IEventSerializer(Protocol[IType, RType]):
    __slots__ = ()

    def encode(self, event: Event) -> RType:
        """
        Encode an event

        :param event: Event to encode
        :type event: Event
        :return: Encoded event
        :rtype: RType
        """
        ...

    def decode(self, event: IType) -> Event:
        """
        Decode an event

        :param event: Event to decode
        :type event: IType
        :return: Decoded event
        :rtype: Event
        """
        ...


class IProducer(Protocol):
    __slots__ = ()

    def __init__(self, ecore: IECore, **kwargs: Any):
        """
        Construct producer instance

        :param ecore: Event core instance
        :type ecore: IECore
        :param kwargs: Any extra kwargs
        :type kwargs: Dict[str, Extra]
        """
        ...

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        """
        Produce an event

        :param event: Event to produce
        :type event: Event
        :param block: Should I/O be blocked if some delay occurs.
            Defaults to `True`.
        :type block: bool
        :param timeout: Number of seconds to wait in case of latency.
            Defaults to `5`.
        :type timeout: int
        :return: None
        :rtype: None
        """
        ...


class IStream(Protocol):
    __slots__ = ()

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        """
        Put an event to stream

        :param event: Event to put
        :type event: Event
        :param block: Should I/O be blocked if some delay occurs.
            Defaults to `True`.
        :type block: bool
        :param timeout: Number of seconds to wait in case of latency.
            Defaults to `5`.
        :type timeout: int
        :return: None
        :rtype: None
        """
        ...

    def pop(
        self,
        event: EventType,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        """
        Pop an event from stream

        :param event: Event type
        :type event: EventType
        :param block: Should I/O be blocked if some delay occurs.
            Defaults to `True`.
        :type block: bool
        :param timeout: Number of seconds to wait in case of latency.
            Defaults to `5`.
        :type timeout: int
        :return: Next unprocessed event in stream
        :rtype: Event
        """
        ...


class IRunner(Protocol):
    __slots__ = ()

    def __init__(
        self,
        stream: IStream,
        event: EventType,
        *consumers: IConsumer,
    ) -> None:
        """
        Construct runner instance

        :param stream: Event stream
        :type stream: IStream
        :param event: Event type
        :type event: EventType
        :param consumers: Consumers
        :type consumers: Tuple[IConsumer]
        """
        ...

    def run(self) -> None:
        """
        Start runner

        :return: None
        :rtype: None
        """
        ...


class IConsumer(Protocol):
    __slots__ = ()

    def __init__(self, func: ConsumerFunc) -> None:
        """
        Construct consumer instance

        :param func: Consumer function
        :type func: ConsumerFunc
        """
        ...

    def consume(self, event: Event) -> None:
        """
        Consume an event with consumer function

        :param event: Event to consume
        :type event: Event
        :return: None
        :rtype: None
        """
        ...
