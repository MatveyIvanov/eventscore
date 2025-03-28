import importlib
import inspect
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple, Type

from eventscore.core.abstract import (
    ConsumerFunc,
    ConsumerGroup,
    EventType,
    IECore,
    IProcessPipeline,
    IProducer,
    ISpawnWorker,
    IStream,
)
from eventscore.core.exceptions import AlreadySpawnedError
from eventscore.core.pipelines import Pipeline, PipelineItem, ProcessPipeline
from eventscore.core.producers import Producer
from eventscore.core.types import Event
from eventscore.core.workers import SpawnMPWorker, Worker
from eventscore.decorators import consumer as _consumer


class ECore(IECore):
    def __init__(
        self,
        stream: IStream,
        process_pipeline: IProcessPipeline | None = None,
        process_pipeline_type: Type[IProcessPipeline] = ProcessPipeline,
        process_pipeline_init_kwargs: Mapping[str, Any] | None = None,
        spawn_worker: ISpawnWorker | None = None,
        spawn_worker_type: Type[ISpawnWorker] = SpawnMPWorker,
        spawn_worker_init_kwargs: Mapping[str, Any] | None = None,
        producer: IProducer | None = None,
        producer_type: Type[IProducer] = Producer,
        producer_init_kwargs: Mapping[str, Any] | None = None,
    ) -> None:
        self.__stream = stream
        self.__process_pipeline = process_pipeline
        self.__process_pipeline_type = process_pipeline_type
        self.__process_pipeline_init_kwargs = process_pipeline_init_kwargs
        self.__spawn_worker = spawn_worker
        self.__spawn_worker_type = spawn_worker_type
        self.__spawn_worker_init_kwargs = spawn_worker_init_kwargs
        self.__producer = producer
        self.__producer_type = producer_type
        self.__producer_init_kwargs = producer_init_kwargs
        self.__pipelines: Dict[ConsumerGroup, Pipeline] = defaultdict(Pipeline)
        self.__workers: Tuple[Worker, ...] | None = None
        self.__workers_spawned = False

    @property
    def process_pipeline(self) -> IProcessPipeline:
        if self.__process_pipeline is None:
            self.__process_pipeline = self.__process_pipeline_type(
                **(self.__process_pipeline_init_kwargs or {})
            )
        return self.__process_pipeline

    @property
    def spawn_worker(self) -> ISpawnWorker:
        if self.__spawn_worker is None:
            self.__spawn_worker = self.__spawn_worker_type(
                **(self.__spawn_worker_init_kwargs or {})
            )
        return self.__spawn_worker

    @property
    def producer(self) -> IProducer:
        if self.__producer is None:
            self.__producer = self.__producer_type(
                **(self.__producer_init_kwargs or {})
            )
        return self.__producer

    @property
    def stream(self) -> IStream:
        return self.__stream

    def consumer(
        self,
        func: ConsumerFunc | None = None,
        *,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> ConsumerFunc:
        return _consumer(func, ecore=self, event=event, group=group)

    def register_consumer(
        self,
        func: ConsumerFunc,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> None:
        if self.__workers_spawned:
            raise AlreadySpawnedError
        self.__pipelines[group].items.add(  # type:ignore[index]
            PipelineItem(
                func=func,
                event=event,
                group=group,
                clones=clones,
            )
        )

    def discover_consumers(self, *, root: str | None = None) -> None:
        root = root or os.getcwd()
        path = Path(root)

        def discover_in_module(
            path: Path,
        ) -> Iterable[Tuple[ConsumerFunc, EventType, ConsumerGroup, int]]:
            result = []
            try:
                module = importlib.import_module(str(path))
            except ImportError:
                return result
            for name, obj in inspect.getmembers(module):
                if not inspect.isfunction(obj) or not getattr(
                    obj, "__is_consumer__", False
                ):
                    continue

                result.append(
                    (
                        obj,
                        obj.__consumer_event__,
                        obj.__consumer_group__,
                        obj.__consumer_clones__,
                    )
                )

            return result

        def discover_in_package(
            path: Path,
        ) -> Iterable[Tuple[ConsumerFunc, EventType, ConsumerGroup, int]]:
            if not path.is_dir():
                return discover_in_module(path)
            result = []
            if not list(path.glob("__init__.py")):
                return result

            for obj in path.iterdir():
                obj: Path = obj
                if obj.is_dir():
                    result.extend(discover_in_package(obj))
                    continue

                if not str(obj).endswith(".py"):
                    continue

                result.extend(discover_in_module(obj))

            return result

        for func, event, group, clones in discover_in_package(path):
            self.register_consumer(func, event, group, clones)

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        self.producer.produce(event, block=block, timeout=timeout)

    def spawn_workers(self) -> None:
        if self.__workers_spawned:
            return

        workers = self.__build_workers()
        for worker in workers:
            self.spawn_worker(worker)
        self.__workers_spawned = True

    def __build_workers(self) -> Tuple[Worker, ...]:
        if not self.__workers:
            self.__workers = tuple(
                self.process_pipeline(pipeline, self)
                for pipeline in self.__pipelines.values()
            )

        return self.__workers
