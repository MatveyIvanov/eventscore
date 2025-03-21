from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Set, Type

from eventscore.core.abstract import (
    IConsumer,
    IObserver,
    IProcessPipeline,
    IStream,
    TConsumerGroup,
    TEvent,
    TFunc,
)
from eventscore.core.exceptions import EventsCoreError
from eventscore.core.workers import Worker


@dataclass(frozen=True, slots=True)
class PipelineItem:
    func: TFunc
    event: TEvent
    consumer_group: TConsumerGroup
    clones: int = 1

    def __eq__(self, other: PipelineItem) -> bool:
        return (
            self.func == other.func
            and self.event == other.event
            and self.consumer_group == other.consumer_group
        )


@dataclass(frozen=True, slots=True)
class Pipeline:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    items: Set[PipelineItem] = field(default_factory=set)


class ProcessPipeline(IProcessPipeline):
    def __init__(
        self,
        consumer_type: Type[IConsumer] = Consumer,
        observer_type: Type[IObserver] = Observer,
    ) -> None:
        self.__consumer_type = consumer_type
        self.__observer_type = observer_type

    def __call__(self, pipeline: Pipeline, stream: IStream) -> Worker:
        self.__validate_pipeline(pipeline)
        consumers = self.__make_consumers(pipeline.items)
        observer = self.__make_observer(consumers, stream)
        return Worker(
            uid=pipeline.uid,
            name=str(pipeline.uid),
            clones=pipeline.items.pop().clones,
            observer=observer,
        )

    def __validate_pipeline(self, pipeline: Pipeline) -> None:
        if len(pipeline.items) == 0:
            raise EventsCoreError("Pipeline must have at least one item")
        if len(set(item.clones for item in pipeline.items)) > 1:
            raise EventsCoreError(
                "Pipeline must have the same number of clones for all items"
            )

    def __make_consumers(self, items: Set[PipelineItem]) -> List[IConsumer]:
        result = []
        for item in items:
            result.append(self.__consumer_type(item.func, item.event))

        return result

    def __make_observer(self, consumers: List[IConsumer], stream: IStream) -> IObserver:
        return self.__observer_type(
            stream=stream,
            serializer=serializer,
            *consumers,
        )
