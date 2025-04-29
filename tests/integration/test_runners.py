import multiprocessing as mp
from unittest import mock

import pytest

from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.runners import ObserverRunner


def infinite_stream_factory(events):
    class InfiniteStream:
        def __call__(self, *args, **kwargs):  # imitate factory
            return self

        def pop(*args, **kwargs):
            try:
                return next(events_iter)
            except StopIteration:
                raise EmptyStreamError

    def events_generator():
        for event in events:
            yield event

    events_iter = iter(events_generator())

    return InfiniteStream


def mp_run(
    runner: ObserverRunner,
    counter: mp.Value,
    events_count: int,
    consumers_count: int,
):
    def incr():
        counter.value += 1

    events = tuple(mock.Mock() for _ in range(events_count))
    consumers = tuple(mock.Mock(side_effect=incr) for _ in range(consumers_count))

    runner._ObserverRunner__stream = infinite_stream_factory(events)
    runner._ObserverRunner__consumers = consumers
    runner.run()


@pytest.mark.integration
class TestObserverRunner:
    @pytest.mark.parametrize(
        "events_count,max_events",
        [
            (3, 3),  # Normal case, exactly 3 events
            (
                5,
                3,
            ),  # More events than max_events, should only consume 3 events
        ],
    )
    @pytest.mark.parametrize("consumers_count", (1, 2, 3))
    def test_run_limited(
        self,
        events_count,
        max_events,
        consumers_count,
        mock_factory,
        stream_mock_factory,
    ):
        events = tuple(mock_factory() for _ in range(events_count))
        consumers = tuple(mock_factory() for _ in range(consumers_count))
        runner = ObserverRunner(
            stream_mock_factory(events),
            "event",
            "group",
            *consumers,
            max_events=max_events,
        )

        runner.run()

        expected_calls = min(events_count, max_events)
        for consumer in consumers:
            assert consumer.consume.call_count == expected_calls
            if expected_calls:
                consumer.consume.assert_has_calls(
                    [mock.call(event) for event in events[:expected_calls]]
                )

    @pytest.mark.parametrize(
        "events_count,max_events",
        ((0, 2), (0, 1), (0, -1), (1, -1)),
        ids=(
            "limited-no-events",
            "limited-1-event-short",
            "unlimited-no-events",
            "unlimited-1-event",
        ),
    )
    @pytest.mark.parametrize(
        "consumers_count",
        (1, 2, 3),
        ids=("one-consumer", "two-consumers", "three-consumers"),
    )
    @pytest.mark.parametrize(
        "timeout",
        (0.01, 0.1, 1),
        ids=("ten-milliseconds", "hundred-milliseconds", "second"),
    )
    def test_run_unlimited(
        self,
        events_count,
        max_events,
        consumers_count,
        timeout,
        stream_mock_factory,
        mock_factory,
    ):
        processed_events_counter = mp.Value("i", 0)
        runner = ObserverRunner(
            # just some random picklable,
            # will be changed inside spawned process
            lambda: None,
            "event",
            "group",
            # just some random picklable,
            # will be changed inside spawned process
            None,
            max_events=max_events,
        )
        expected_events_count = max(min(events_count, max_events), 0)

        process = mp.Process(
            target=mp_run,
            args=(runner, processed_events_counter, events_count, consumers_count),
        )
        process.start()
        process.join(timeout)  # Let runner work for some time
        assert process.is_alive()
        process.terminate()
        process.join()
        assert not process.is_alive()
        assert processed_events_counter.value == expected_events_count * consumers_count
