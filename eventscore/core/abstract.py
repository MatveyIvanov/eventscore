from __future__ import annotations

from typing import Protocol, Callable, TypeVar

from eventscore.core.events import Event, TEvent
from eventscore.core.pipelines import Pipeline
from eventscore.core.workers import Worker

TFunc = TypeVar("TFunc", bound=Callable)
TConsumerGroup = TypeVar("TConsumerGroup", bound=str)


class IECore(Protocol):
    __slots__ = ()

    def consumer(
        self,
        func: TFunc | None = None,
        *,
        event: TEvent,
        consumer_group: TConsumerGroup,
        clones: int = 1,
    ) -> TFunc: ...
    def register_consumer(
        self,
        func: TFunc,
        event: TEvent,
        consumer_group: TConsumerGroup,
        clones: int = 1,
    ) -> None: ...
    def spawn_workers(self) -> None: ...
    def run(self) -> None: ...


class IProcessPipeline(Protocol):
    __slots__ = ()

    def __call__(self, pipeline: Pipeline, stream: IStream) -> Worker: ...


class ISpawnWorker(Protocol):
    __slots__ = ()

    def __call__(self, worker: Worker) -> None: ...


class IEventSerializer(Protocol):
    __slots__ = ()

    def decode(self, bevent: bytes) -> Event: ...
    def encode(self, event: Event) -> bytes: ...


class IProducer(Protocol):
    __slots__ = ()

    async def produce(self, event: Event) -> None: ...


class IStream(Protocol):
    __slots__ = ()

    async def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None: ...
    async def pop(
        self,
        event: TEvent,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event: ...


class IObserver(Protocol):
    __slots__ = ()

    def run(self) -> None: ...


class IASyncConsumer(Protocol):
    __slots__ = ()

    async def consume(self, event: Event) -> None: ...


class IConsumer(Protocol):
    __slots__ = ()

    def consume(self, event: Event) -> None: ...
