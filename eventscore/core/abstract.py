from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Any, Callable, Protocol, TypeAlias, TypeVar, Union

from eventscore.core.types import Event, Pipeline, Worker

EventType: TypeAlias = Union[str, StrEnum, IntEnum]
ConsumerFunc: TypeAlias = Callable[[Event], Any]
ConsumerGroup: TypeAlias = Union[str, StrEnum, IntEnum]

IType = TypeVar("IType")
RType = TypeVar("RType")


class IECore(Protocol):
    __slots__ = ()

    @property
    def process_pipeline(self) -> IProcessPipeline: ...
    @property
    def spawn_worker(self) -> ISpawnWorker: ...
    @property
    def producer(self) -> IProducer: ...
    @property
    def stream(self) -> IStream: ...

    def consumer(
        self,
        func: ConsumerFunc | None = None,
        *,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> ConsumerFunc: ...

    def register_consumer(
        self,
        func: ConsumerFunc,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> None: ...
    def discover_consumers(self, *, package: str | None = None) -> None: ...

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None: ...
    def spawn_workers(self) -> None: ...


class IProcessPipeline(Protocol):
    __slots__ = ()

    def __call__(self, pipeline: Pipeline, ecore: IECore) -> Worker: ...


class ISpawnWorker(Protocol):
    __slots__ = ()

    def __call__(self, worker: Worker) -> None: ...


class IEventSerializer(Protocol[IType, RType]):
    __slots__ = ()

    def encode(self, event: Event) -> RType: ...
    def decode(self, event: IType) -> Event: ...


class IProducer(Protocol):
    __slots__ = ()

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None: ...


class IStream(Protocol):
    __slots__ = ()

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None: ...

    def pop(
        self,
        event: EventType,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event: ...


class IRunner(Protocol):
    __slots__ = ()

    def __init__(
        self,
        stream: IStream,
        event: EventType,
        *consumers: IConsumer,
    ) -> None: ...
    def run(self) -> None: ...


class IConsumer(Protocol):
    __slots__ = ()

    def __init__(self, func: ConsumerFunc) -> None: ...
    def consume(self, event: Event) -> None: ...
