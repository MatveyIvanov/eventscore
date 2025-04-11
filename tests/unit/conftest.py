from unittest import mock

import pytest

from eventscore.core.consumers import Consumer
from eventscore.core.pipelines import ProcessPipeline
from eventscore.core.producers import Producer
from eventscore.core.runners import ObserverRunner
from eventscore.core.serializers import EventSerializer
from eventscore.core.types import Event, Pipeline, Worker
from eventscore.core.workers import SpawnMPWorker


@pytest.fixture
def event():
    return Event(type="event")


@pytest.fixture
def pipeline_factory():
    def factory(uid=None, items=None):
        kwargs = {}
        if uid is not None:
            kwargs["uid"] = uid
        if items is not None:
            kwargs["items"] = items
        return Pipeline(**kwargs)

    return factory


@pytest.fixture
def worker_factory(runner_mock):
    def factory(clones: int) -> Worker:
        return Worker(
            name="name",
            clones=clones,
            runner=runner_mock,
        )

    return factory


@pytest.fixture
def consumer_func_mock():
    return mock.Mock()


@pytest.fixture
def ecore_mock():
    ecore = mock.Mock()
    return ecore


@pytest.fixture
def consumer_mock():
    return mock.Mock()


@pytest.fixture
def runner_mock():
    return mock.Mock()


@pytest.fixture
def stream_mock(event):
    stream = mock.Mock()
    stream.put.return_value = None
    stream.pop.return_value = event
    return stream


@pytest.fixture
def mp_process_mock():
    return mock.Mock()


@pytest.fixture
def mp_mock(mp_process_mock):
    mp = mock.Mock()
    mp.Process.return_value = mp_process_mock
    return mp


@pytest.fixture
def threading_thread_mock():
    return mock.Mock()


@pytest.fixture
def threading_mock(threading_thread_mock):
    threading = mock.Mock()
    threading.Thread.return_value = threading_thread_mock
    return threading


@pytest.fixture
def consumer(consumer_func_mock):
    return Consumer(consumer_func_mock)


@pytest.fixture
def producer(ecore_mock):
    return Producer(ecore_mock)


@pytest.fixture
def spawn_mp_worker():
    return SpawnMPWorker()


@pytest.fixture
def observer_runner_factory(stream_mock):
    def factory(event, max_events, *consumers):
        return ObserverRunner(stream_mock, event, max_events, *consumers)

    return factory


@pytest.fixture
def process_pipeline(consumer_mock, runner_mock):
    return ProcessPipeline(consumer_mock, runner_mock)


@pytest.fixture
def event_serializer():
    return EventSerializer()
