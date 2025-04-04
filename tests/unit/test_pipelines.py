from unittest import mock

import pytest

from eventscore.core.exceptions import (
    EmptyPipelineError,
    ClonesMismatchError,
    UnrelatedConsumersError,
)
from eventscore.core.types import Worker, PipelineItem


class TestProcessPipeline:
    @pytest.mark.parametrize(
        "items,expected_error,expected_clones,expected_event",
        (
            ([], EmptyPipelineError, None, None),
            (
                [
                    PipelineItem(func=int, event="event", group="group", clones=1),
                    PipelineItem(func=int, event="event", group="group", clones=2),
                ],
                ClonesMismatchError,
                None,
                None,
            ),
            (
                [
                    PipelineItem(func=int, event="event1", group="group", clones=1),
                    PipelineItem(func=int, event="event2", group="group", clones=1),
                ],
                UnrelatedConsumersError,
                None,
                None,
            ),
            (
                [PipelineItem(func=int, event="event", group="group", clones=1)],
                None,
                1,
                "event",
            ),
            (
                [
                    PipelineItem(func=int, event="ev", group="group", clones=2),
                    PipelineItem(func=int, event="ev", group="group", clones=2),
                ],
                None,
                2,
                "ev",
            ),
        ),
    )
    def test_process(
        self,
        items,
        expected_error,
        expected_clones,
        expected_event,
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
            consumer_mock.assert_has_calls([mock.call(item.func) for item in items])
            runner_mock.assert_called_once_with(
                ecore_mock.stream,
                expected_event,
                *[consumer_mock.return_value for _ in items],
            )
