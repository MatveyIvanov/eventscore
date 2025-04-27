from __future__ import annotations

import logging

from eventscore.core.abstract import (
    ConsumerGroup,
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
from eventscore.core.logging import logger as _logger
from eventscore.core.runners import ObserverRunner
from eventscore.core.types import Pipeline, PipelineItem
from eventscore.core.workers import Worker


class ProcessPipeline(IProcessPipeline):
    def __init__(
        self,
        consumer_type: type[IConsumer] = Consumer,
        runner_type: type[IRunner] = ObserverRunner,
        logger: logging.Logger = _logger,
    ) -> None:
        self.__consumer_type = consumer_type
        self.__runner_type = runner_type
        self.__logger = logger

    def __call__(self, pipeline: Pipeline, ecore: IECore) -> Worker:
        event, group, clones = self.__validate_pipeline(pipeline)
        self.__logger.debug(
            f"Received valid pipeline {pipeline}. Event: {event}. Clones: {clones}"
        )
        consumers = self.__make_consumers(pipeline.items)
        self.__logger.debug(f"Built consumers: {consumers}")
        runner = self.__make_runner(consumers, ecore, event, group)
        self.__logger.debug(f"Built runner: {runner}")
        return Worker(
            uid=pipeline.uid,
            name=str(pipeline.uid),
            clones=clones,
            runner=runner,
        )

    def __validate_pipeline(
        self,
        pipeline: Pipeline,
    ) -> tuple[EventType, ConsumerGroup, int]:
        if len(pipeline.items) == 0:
            raise EmptyPipelineError

        clones_unique = set(item.clones for item in pipeline.items)
        if len(clones_unique) > 1:
            raise ClonesMismatchError
        events_unique = set(item.event for item in pipeline.items)
        if (len(events_unique)) > 1:
            raise UnrelatedConsumersError

        return (
            events_unique.pop(),
            next(iter(pipeline.items)).group,
            clones_unique.pop(),
        )

    def __make_consumers(self, items: set[PipelineItem]) -> list[IConsumer]:
        result: list[IConsumer] = []
        for item in items:
            result.append(self.__consumer_type(item.func, logger=self.__logger))

        return result

    def __make_runner(
        self,
        consumers: list[IConsumer],
        ecore: IECore,
        event: EventType,
        group: ConsumerGroup,
    ) -> IRunner:
        return self.__runner_type(
            ecore.stream,
            event,
            group,
            *consumers,
            logger=self.__logger,
        )
