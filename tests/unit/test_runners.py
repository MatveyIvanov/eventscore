from unittest import mock

import pytest

from eventscore.core.exceptions import EmptyStreamError


class TestObserverRunner:
    @pytest.mark.parametrize(
        "max_events,consumers,expect_error",
        (
            (-1, [], True),
            (-1, ["consumer"], False),
            (-1, ["c1", "c2"], False),
            (0, [], True),
            (0, ["consumer"], True),
            (1, ["c1", "c2"], False),
            (1, [], True),
            (1, ["consumer"], False),
            (1, ["c1", "c2"], False),
        ),
    )
    def test_init(self, max_events, consumers, expect_error, observer_runner_factory):
        if expect_error:
            with pytest.raises(AssertionError):
                observer_runner_factory("event", max_events, *consumers)
        else:
            observer_runner_factory("event", max_events, *consumers)

    @pytest.mark.parametrize(
        "events,max_events,expected_events_to_process",
        # NOTE: max_events must be <= len(events), otherwise infinite loop will be started.
        # TODO: some tests with timeouts to test infinite loops could be considered.
        (
            (["event"], 1, 1),
            (["e1", "e2"], 1, 1),
            (["e1", "e2"], 2, 2),
            (["event", EmptyStreamError], 1, 1),
            ([EmptyStreamError, "event"], 1, 1),
            (["e1", EmptyStreamError, "e2"], 1, 1),
            (["e1", EmptyStreamError, "e2"], 2, 2),
        ),
    )
    @pytest.mark.parametrize(
        "consumers",
        (
            [mock.Mock()],
            [mock.Mock(), mock.Mock()],
            [mock.Mock(), mock.Mock(), mock.Mock()],
        ),
    )
    def test_run(
        self,
        events,
        max_events,
        expected_events_to_process,
        consumers,
        stream_mock,
        observer_runner_factory,
        threading_mock,
        threading_thread_mock,
    ):
        events_to_pop = events.copy()
        expected_events_to_process_lst = list(
            event for event in events if event != EmptyStreamError
        )[:expected_events_to_process]

        def pop(*args, **kwargs):
            if not events_to_pop:
                raise EmptyStreamError

            event = events_to_pop.pop(0)
            if event == EmptyStreamError:
                raise event

            return event

        stream_mock.pop.side_effect = pop
        (
            expected_stream_pop_calls,
            expected_thread_calls,
            expected_start_calls,
            expected_join_calls,
        ) = (
            [mock.call("event", block=True) for _ in range(expected_events_to_process)],
            [],
            [],
            [],
        )
        for event in expected_events_to_process_lst:
            for consumer in consumers:
                expected_thread_calls.append(
                    mock.call(
                        target=consumer.consume,
                        args=(event,),
                    )
                )
                expected_start_calls.append(mock.call())
                expected_join_calls.append(mock.call())

        with mock.patch("eventscore.core.runners.threading", threading_mock):
            observer_runner_factory("event", max_events, *consumers).run()

        threading_mock.Thread.assert_has_calls(expected_thread_calls)
        threading_thread_mock.start.assert_has_calls(expected_start_calls)
        threading_thread_mock.join.assert_has_calls(expected_join_calls)
