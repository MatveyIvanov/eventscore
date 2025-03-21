from collections import defaultdict
from typing import Dict, Tuple

from eventscore.core.abstract import (
    IECore,
    TFunc,
    TEvent,
    TConsumerGroup,
    IProcessPipeline,
    ISpawnWorker,
)
from eventscore.core.pipelines import Pipeline, PipelineItem, ProcessPipeline
from eventscore.core.workers import Worker, SpawnMPWorker
from eventscore.decorators import consumer as _consumer


class ECore(IECore):
    def __init__(
        self,
        process_pipeline: IProcessPipeline = ProcessPipeline,
        spawn_worker: ISpawnWorker = SpawnMPWorker,
    ) -> None:
        self.__process_pipeline = process_pipeline
        self.__spawn_worker = spawn_worker
        self.__pipelines: Dict[TConsumerGroup, Pipeline] = defaultdict(Pipeline)
        self.__workers = {}
        self.__workers_spawned = False

    def consumer(
        self,
        func: TFunc | None = None,
        *,
        event: TEvent,
        consumer_group: TConsumerGroup,
        clones: int = 1,
    ) -> TFunc:
        return _consumer(func, ecore=self, event=event, consumer_group=consumer_group)

    def register_consumer(
        self,
        func: TFunc,
        event: TEvent,
        consumer_group: TConsumerGroup,
        clones: int = 1,
    ) -> None:
        self.__pipelines[consumer_group].items.add(
            PipelineItem(
                func=func,
                event=event,
                consumer_group=consumer_group,
                clones=clones,
            )
        )

    def spawn_workers(self) -> None:
        if self.__workers_spawned:
            return

        workers = self._build_workers()
        for worker in workers:
            self.__spawn_worker(worker)
        self.__workers_spawned = True

    def _build_workers(self) -> Tuple[Worker, ...]:
        if not self.__workers:
            self.__workers = tuple(
                self.__process_pipeline(pipeline)
                for pipeline in self.__pipelines.values()
            )

        return self.__workers
