from unittest import mock

import pytest

from eventscore.core.consumers import Consumer
from eventscore.core.ecore import ECore
from eventscore.core.pipelines import ProcessPipeline
from eventscore.core.producers import Producer
from eventscore.core.runners import ObserverRunner
from eventscore.core.serializers import EventSerializer
from eventscore.core.types import Event, Pipeline, Worker
from eventscore.core.workers import SpawnMPWorker
from eventscore.ext.redis.serializers import RedisEventSerializer
from eventscore.ext.redis.streams import RedisStream


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
    def factory(clones=1):
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
def process_pipeline_mock(worker_factory):
    return mock.Mock(return_value=worker_factory())


@pytest.fixture
def spawn_worker_mock():
    return mock.Mock()


@pytest.fixture
def producer_mock():
    return mock.Mock()


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
def redis_mock():
    redis = mock.Mock()
    redis.return_value = redis
    redis.xread.return_value = [
        (
            b"event",
            (
                (
                    b"uid",
                    {b"value": b"data"},
                )
            ),
        )
    ]
    return redis


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
    def factory(
        event,
        *consumers,
        max_events=-1,
        logger=SKIP,
    ):
        kwargs = {"max_events": max_events}
        if logger != SKIP:
            kwargs["logger"] = logger
        print(consumers)
        return ObserverRunner(
            stream_mock,
            event,
            *consumers,
            **kwargs,
        )

    return factory


@pytest.fixture
def process_pipeline(consumer_mock, runner_mock):
    return ProcessPipeline(consumer_mock, runner_mock)


@pytest.fixture
def event_serializer():
    return EventSerializer()


@pytest.fixture
def redis_event_serializer():
    return RedisEventSerializer()


class _SKIP:
    def __bool__(self):
        return False


SKIP = _SKIP()
SELF = "self"


@pytest.fixture
def ecore_factory(stream_mock, process_pipeline_mock, spawn_worker_mock, producer_mock):
    def factory(
        stream=stream_mock,
        process_pipeline=process_pipeline_mock,
        process_pipeline_type=ProcessPipeline,
        process_pipeline_init_kwargs=None,
        spawn_worker=spawn_worker_mock,
        spawn_worker_type=SpawnMPWorker,
        spawn_worker_init_kwargs=None,
        producer=producer_mock,
        producer_type=Producer,
        producer_init_kwargs=None,
        logger=SKIP,
        kwdefaults_overrides=None,
    ):
        kwargs = {}
        if stream != SKIP:
            kwargs["stream"] = stream
        if process_pipeline != SKIP:
            kwargs["process_pipeline"] = process_pipeline
        if process_pipeline_type != SKIP:
            kwargs["process_pipeline_type"] = process_pipeline_type
        if process_pipeline_init_kwargs != SKIP:
            kwargs["process_pipeline_init_kwargs"] = process_pipeline_init_kwargs
        if spawn_worker != SKIP:
            kwargs["spawn_worker"] = spawn_worker
        if spawn_worker_type != SKIP:
            kwargs["spawn_worker_type"] = spawn_worker_type
        if spawn_worker_init_kwargs != SKIP:
            kwargs["spawn_worker_init_kwargs"] = spawn_worker_init_kwargs
        if producer != SKIP:
            kwargs["producer"] = producer
        if producer_type != SKIP:
            kwargs["producer_type"] = producer_type
        if producer_init_kwargs != SKIP:
            kwargs["producer_init_kwargs"] = producer_init_kwargs
        if logger != SKIP:
            kwargs["logger"] = logger

        if kwdefaults_overrides:
            kwdefaults = ECore.__init__.__kwdefaults__
            kwdefaults.update(kwdefaults_overrides)
            with mock.patch.object(ECore.__init__, "__kwdefaults__", kwdefaults):
                return ECore(**kwargs)
        return ECore(**kwargs)

    return factory


@pytest.fixture
def consumer_decorator_mock():
    return mock.Mock()


@pytest.fixture
def event_serializer_mock():
    return mock.Mock()


@pytest.fixture
def redis_stream_factory(redis_mock, event_serializer_mock):
    def factory(
        redis=redis_mock,
        host="redis",
        port=6379,
        db=0,
        redis_init_kwargs=None,
    ):
        kwargs = {}
        if redis != SKIP:
            kwargs["redis"] = redis
        if host != SKIP:
            kwargs["host"] = host
        if port != SKIP:
            kwargs["port"] = port
        if db != SKIP:
            kwargs["db"] = db
        if redis_init_kwargs != SKIP:
            kwargs["redis_init_kwargs"] = redis_init_kwargs
        return RedisStream(serializer=event_serializer_mock, **kwargs)

    return factory
