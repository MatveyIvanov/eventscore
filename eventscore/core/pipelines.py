from __future__ import annotations

from typing import List, Set, Type

from eventscore.core.abstract import (
    EventType,
    IConsumer,
    IECore,
    IProcessPipeline,
    IRunner,
)
from eventscore.core.consumers import Consumer
from eventscore.core.exceptions import (
    ClonesMismatchError,
    EmptyPipelineError,
    UnrelatedConsumersError,
)
from eventscore.core.logging import logger
from eventscore.core.runners import ObserverRunner
from eventscore.core.types import Pipeline, PipelineItem
from eventscore.core.workers import Worker


class ProcessPipeline(IProcessPipeline):
    def __init__(
        self,
        consumer_type: Type[IConsumer] = Consumer,
        runner_type: Type[IRunner] = ObserverRunner,
    ) -> None:
        self.__consumer_type = consumer_type
        self.__runner_type = runner_type
        self.__logger = logger

    def __call__(self, pipeline: Pipeline, ecore: IECore) -> Worker:
        self.__validate_pipeline(pipeline)
        self.__logger.debug(f"Received valid pipeline {pipeline}.")
        event = self.__get_event(pipeline.items)
        self.__logger.debug(f"Pipeline has event {event}.")
        consumers = self.__make_consumers(pipeline.items)
        self.__logger.debug(f"Built consumers: {consumers}")
        runner = self.__make_runner(consumers, ecore, event)
        self.__logger.debug(f"Built runner: {runner}")
        return Worker(
            uid=pipeline.uid,
            name=str(pipeline.uid),
            clones=pipeline.items.pop().clones,
            runner=runner,
        )

    def __validate_pipeline(self, pipeline: Pipeline) -> None:
        if len(pipeline.items) == 0:
            raise EmptyPipelineError
        if len(set(item.clones for item in pipeline.items)) > 1:
            raise ClonesMismatchError
        if (len(set(item.event for item in pipeline.items))) > 1:
            raise UnrelatedConsumersError

    def __get_event(self, items: Set[PipelineItem]) -> EventType:
        return next(iter(items)).event

    def __make_consumers(self, items: Set[PipelineItem]) -> List[IConsumer]:
        result = []
        for item in items:
            result.append(self.__consumer_type(item.func))

        return result

    def __make_runner(
        self,
        consumers: List[IConsumer],
        ecore: IECore,
        event: EventType,
    ) -> IRunner:
        return self.__runner_type(ecore.stream, event, *consumers)
