import multiprocessing as mp
import random

import pytest

from eventscore.core.abstract import IStreamFactory
from eventscore.core.exceptions import EventsCoreError
from eventscore.core.types import ConsumerGroup, Event, EventType
from tests.integration.conftest import override_mp_start_method


def pop_from_stream(
    factory: IStreamFactory,
    event: EventType,
    group: ConsumerGroup,
    count: int,
) -> list[Event]:
    stream = factory()
    result = []
    for _ in range(count):
        try:
            result.append(stream.pop(event, group))
        except EventsCoreError:
            continue
    return result


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.concurrency
@pytest.mark.redis
class TestRedisStreams:
    @pytest.mark.parametrize(
        "eventset,eventrandrange,event_n_group_to_clones",
        (
            (
                {"event1", "event2"},
                (1, 2),
                {("event1", "group1"): 1, ("event2", "group2"): 1},
            ),
            (
                {"event1", "event2"},
                (1, 2),
                {("event1", "group1"): 2, ("event2", "group2"): 2},
            ),
            (
                {"event1", "event2"},
                (5, 10),
                {("event1", "group1"): 1, ("event2", "group2"): 1},
            ),
            (
                {"event1", "event2"},
                (5, 10),
                {("event1", "group1"): 2, ("event2", "group2"): 2},
            ),
            (
                {"event1", "event2"},
                (25, 50),
                {("event1", "group1"): 1, ("event2", "group2"): 1},
            ),
            (
                {"event1", "event2"},
                (25, 50),
                {("event1", "group1"): 2, ("event2", "group2"): 2},
            ),
            (
                {"event1", "event2", "event3", "event4", "event5"},
                (1, 2),
                {
                    ("event1", "group1"): 1,
                    ("event2", "group2"): 1,
                    ("event3", "group3"): 1,
                    ("event4", "group4"): 1,
                    ("event5", "group5"): 1,
                },
            ),
            (
                {"event1", "event2", "event3", "event4", "event5"},
                (1, 2),
                {
                    ("event1", "group1"): 2,
                    ("event2", "group2"): 3,
                    ("event3", "group3"): 4,
                    ("event4", "group4"): 3,
                    ("event5", "group5"): 2,
                },
            ),
            (
                {"event1", "event2", "event3", "event4", "event5"},
                (5, 10),
                {
                    ("event1", "group1"): 1,
                    ("event2", "group2"): 1,
                    ("event3", "group3"): 1,
                    ("event4", "group4"): 1,
                    ("event5", "group5"): 1,
                },
            ),
            (
                {"event1", "event2", "event3", "event4", "event5"},
                (5, 10),
                {
                    ("event1", "group1"): 2,
                    ("event2", "group2"): 3,
                    ("event3", "group3"): 4,
                    ("event4", "group4"): 3,
                    ("event5", "group5"): 2,
                },
            ),
        ),
    )
    @pytest.mark.parametrize(
        "repeats",
        (1, 2, 3),
        ids=("first", "second", "third"),
    )
    @pytest.mark.parametrize("mp_start_method", ("fork", "spawn"))
    def test_pop_concurrency(
        self,
        eventset,
        eventrandrange,
        event_n_group_to_clones,
        repeats,
        mp_start_method,
        redis_stream_factory,
    ):
        """
        It was not obvious, which test-cases would fit testing requirements.
        I know it does not look perfect,
        but is there any guaranteed ways to test concurrency after all?
        Randomness seems good enough to test consurrency issues.

        Yeah, really slow, but VERY important to not have any concurrency issues
        """
        with override_mp_start_method(mp_start_method):
            stream = redis_stream_factory()
            expected_ids = set()
            event_to_count: dict[str, int] = dict()
            for event in eventset:
                count = random.randint(*eventrandrange)
                for _ in range(count):
                    instance = Event(type=event)
                    stream.put(instance)
                    expected_ids.add(instance.uid)
                event_to_count[event] = count

            pool, results = mp.Pool(), []
            # For each consumer group
            for event, group in event_n_group_to_clones.keys():
                # For each clone
                for _ in range(event_n_group_to_clones[(event, group)]):
                    results.append(
                        pool.apply_async(
                            pop_from_stream,
                            args=(
                                redis_stream_factory,
                                event,
                                group,
                                event_to_count[event],
                            ),
                        )
                    )
            pool.close()
            pool.join()
            ids = []
            for result in results:
                assert result.ready()
                assert result.successful()
                ids.extend(item.uid for item in result.get())

            ids_unique = set(ids)
            assert len(ids) == len(ids_unique)
            assert len(ids) == len(expected_ids)
            assert ids_unique == expected_ids
