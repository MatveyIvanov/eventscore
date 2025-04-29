from unittest import mock

import pytest

from eventscore.core.exceptions import (
    ClonesMismatchError,
    EmptyPipelineError,
    UnrelatedConsumersError,
)
from eventscore.core.logging import logger as _logger
from eventscore.core.types import PipelineItem, Worker


@pytest.mark.unit
class TestProcessPipeline:
    @pytest.mark.parametrize(
        "items,expected_error,expected_clones,expected_event,expected_group",
        (
            ([], EmptyPipelineError, None, None, None),
            (
                [
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="event",
                        group="group",
                        clones=1,
                    ),
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="event",
                        group="group",
                        clones=2,
                    ),
                ],
                ClonesMismatchError,
                None,
                None,
                None,
            ),
            (
                [
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="event1",
                        group="group",
                        clones=1,
                    ),
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="event2",
                        group="group",
                        clones=1,
                    ),
                ],
                UnrelatedConsumersError,
                None,
                None,
                None,
            ),
            (
                [
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="event",
                        group="group",
                        clones=1,
                    )
                ],
                None,
                1,
                "event",
                "group",
            ),
            (
                [
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="ev",
                        group="group",
                        clones=2,
                    ),
                    PipelineItem(
                        func=int,
                        func_path="path",
                        event="ev",
                        group="group",
                        clones=2,
                    ),
                ],
                None,
                2,
                "ev",
                "group",
            ),
        ),
        ids=(
            "empty-pipeline",
            "clones-mismatch",
            "unrelated-consumers",
            "single-item",
            "multiple-items",
        ),
    )
    def test_process(
        self,
        items,
        expected_error,
        expected_clones,
        expected_event,
        expected_group,
        pipeline_factory,
        ecore_mock,
        consumer_mock,
        runner_mock,
        process_pipeline,
    ):
        pipeline = pipeline_factory(items=items)

        if expected_error:
            with pytest.raises(expected_error):
                process_pipeline(pipeline, ecore_mock)

                consumer_mock.assert_not_called()
                runner_mock.assert_not_called()
        else:
            result = process_pipeline(pipeline, ecore_mock)

            assert isinstance(result, Worker)
            assert result.uid == pipeline.uid
            assert result.name == str(pipeline.uid)
            assert result.clones == expected_clones
            assert result.runner == runner_mock.return_value
            consumer_mock.assert_has_calls(
                [mock.call(item.func, logger=_logger) for item in items]
            )
            runner_mock.assert_called_once_with(
                ecore_mock.stream_factory,
                expected_event,
                expected_group,
                *[consumer_mock.return_value for _ in items],
                logger=_logger,
            )
