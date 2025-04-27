from __future__ import annotations

import logging
from collections.abc import Callable
from enum import IntEnum, StrEnum
from typing import Any, Protocol, TypeAlias, TypeVar

from eventscore.core.logging import logger as _logger
from eventscore.core.types import Event, Pipeline, Worker

# Type alias for user-defined event type
EventType: TypeAlias = str | StrEnum | IntEnum
# Type alias for user-defined consumer functions/other callable
ConsumerFunc: TypeAlias = Callable[[Event], Any]
# Type alias for user-defined consumer group
ConsumerGroup: TypeAlias = str | StrEnum | IntEnum
# Type alias for number of clones
NumberOfClones: TypeAlias = int
# Type alias for path to consumer function's module
FunctionModulePath: TypeAlias = str

# Type variable for serializer input
IType = TypeVar("IType", contravariant=True)
# Type variable for serializer output
RType = TypeVar("RType", covariant=True)


class IECore(Protocol):
    """
    Event core class.
    Can be used for:
        * Accessing pipeline processor
        * Accessing worker spawner
        * Accessing producer
        * Accessing event stream
        * Decorating functions to make them consumers
        * Registering functions to make them consumers
        * Discovering consumers marked with @(ecore.)consumer decorator
        * Producing events
        * Spawning workers bulit from registered consumers
    """

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
        clones: NumberOfClones = 1,
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
        :type clones: NumberOfClones
        :return: Decorated function
        :rtype: ConsumerFunc
        """
        ...

    def register_consumer(
        self,
        func: ConsumerFunc,
        event: EventType,
        group: ConsumerGroup,
        *,
        clones: NumberOfClones = 1,
        func_path: str | None = None,
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
        :type clones: NumberOfClones
        :param func_path: Path (absolute preferred)
            to module where function is defined.
            Is used for consumer functions equality check
            to avoid duplicate registering.
            Defaults to
            ```
            (inspect.getsourcefile(func) or "") + ":" + func.__name__
            ```
        :type func_path: str | None
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
    """
    Pipeline processor class.
    One and only purpose of this class is to build worker
    based on a given pipeline.
    """

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
    """
    Worker spawner class.
    One and only purpose of this class is to spawn a given worker.
    """

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
    """
    Event serializer class.
    One and only purpose of this class is to encode and decode events.
    """

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
    """
    Producer class.
    One and only purpose of this class is to produce events.
    """

    __slots__ = ()

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
    """
    Event stream class.
    One and only purpose of this class is to put and pop events.
    """

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
        group: ConsumerGroup,
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
    """
    Runner class.
    One and only purpose of this class is to run given consumers.

    :param stream: Event stream
    :type stream: IStream
    :param event: Event type
    :type event: EventType
    :param consumers: Consumers
    :type consumers: Tuple[IConsumer, ...]
    :param max_events: Max events to process
        Defaults to -1.
        If value is equal to -1,
        then there is not limit for number of events to process
    :type max_events: int
    :param logger: Logger instance
    :type logger: logging.Logger
    """

    __slots__ = ()

    def __init__(
        self,
        stream: IStream,
        event: EventType,
        group: ConsumerGroup,
        *consumers: IConsumer,
        max_events: int = -1,
        logger: logging.Logger = _logger,
    ) -> None: ...

    def run(self) -> None:
        """
        Start runner

        :return: None
        :rtype: None
        """
        ...


class IConsumer(Protocol):
    """
    Consumer class.
    One and only purpose of this class is to consume events.
    """

    __slots__ = ()

    def __init__(self, func: ConsumerFunc, logger: logging.Logger = _logger) -> None:
        """
        Construct consumer instance

        :param func: Consumer function
        :type func: ConsumerFunc
        :param logger: Logger instance
        :type logger: logging.Logger
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
