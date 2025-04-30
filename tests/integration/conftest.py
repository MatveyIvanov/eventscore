import multiprocessing as mp
import os
from contextlib import contextmanager
from typing import Iterator, Literal
from unittest import mock

import pytest
from dotenv import load_dotenv

from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.streams import StreamFactory
from eventscore.ext.redis.serializers import RedisEventSerializer
from eventscore.ext.redis.streams import RedisStream


@contextmanager
def override_mp_start_method(method: Literal["fork", "spawn"]) -> Iterator[None]:
    orig_method = mp.get_start_method()
    mp.set_start_method(method, force=True)
    try:
        yield
    finally:
        mp.set_start_method(orig_method, force=True)


@pytest.fixture(scope="session")
def envs():
    return {
        "tests/integration/.env",
        "tests/integration/redis/.env",
    }


@pytest.fixture(scope="session", autouse=True)
def load_env(envs):
    pwd = os.getcwd()
    for env in envs:
        for dir in env.split("/")[:-1]:
            pwd = pwd.replace("/" + dir, "")
        _ = load_dotenv(pwd + "/" + env, verbose=True, override=True)


@pytest.fixture(scope="session")
def redis_serializer():
    return RedisEventSerializer()


@pytest.fixture
def redis_stream_factory(redis_serializer):
    return StreamFactory(
        stream_class=RedisStream,
        kwargs={
            "serializer": redis_serializer,
            "host": os.environ["REDIS_HOST"],
            "port": os.environ["REDIS_PORT"],
            "db": os.environ["REDIS_DB"],
            "redis_init_kwargs": {
                "password": os.environ["REDIS_PASSWORD"],
            },
        },
    )


@pytest.fixture
def stream_mock_factory():
    def factory(events):
        def pop(*args, **kwargs):
            try:
                return next(events_iter)
            except StopIteration:
                raise EmptyStreamError

        def events_generator():
            for event in events:
                yield event

        events_iter = iter(events_generator())

        stream = mock.Mock()
        stream.return_value = stream  # imitate factory
        stream.pop.side_effect = pop
        return stream

    return factory
