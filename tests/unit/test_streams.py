import os
from unittest import mock

import pytest
from redis import ResponseError

from eventscore.core.exceptions import EmptyStreamError, TooManyDataError
from tests.unit.conftest import SKIP


@pytest.mark.unit
class TestRedisStream:
    @pytest.mark.parametrize("redis", (SKIP, None, "redis_mock"))
    @pytest.mark.parametrize("host", (SKIP, None, "redis"))
    @pytest.mark.parametrize("port", (SKIP, None, 6379))
    @pytest.mark.parametrize("db", (SKIP, None, 1))
    @pytest.mark.parametrize(
        "redis_init_kwargs",
        (
            SKIP,
            None,
            {},
            {"password": "password"},
            {"host": "newhost", "port": 1111, "db": 2},
        ),
    )
    def test_init(
        self,
        redis,
        host,
        port,
        db,
        redis_init_kwargs,
        redis_event_serializer,
        redis_mock,
        redis_stream_factory,
    ):
        expect_redis_init, expect_error = (
            not bool(redis),
            not redis and (not host or not port or not db),
        )
        expected_redis_init_kwargs = redis_init_kwargs or {}
        expected_redis_init_kwargs.update(
            {"host": host or None, "port": port or None, "db": db or None}
        )
        redis = redis_mock if redis else redis
        with mock.patch("eventscore.ext.redis.streams.Redis", redis_mock):
            if expect_error:
                with pytest.raises(AssertionError):
                    redis_stream_factory(
                        redis=redis,
                        host=host,
                        port=port,
                        db=db,
                        redis_init_kwargs=redis_init_kwargs,
                    )

                redis_mock.assert_not_called()
            else:
                redis_stream_factory(
                    redis=redis,
                    host=host,
                    port=port,
                    db=db,
                    redis_init_kwargs=redis_init_kwargs,
                )

                if expect_redis_init:
                    redis_mock.assert_called_once_with(**expected_redis_init_kwargs)
                else:
                    redis_mock.assert_not_called()

    @pytest.mark.parametrize(
        "block",
        (SKIP, False, True),
        ids=("blocking-by-default", "non-blocking", "blocking"),
    )
    @pytest.mark.parametrize(
        "timeout,expected_timeout",
        ((SKIP, 5), (0, 0)),
        ids=("default-timeout", "no-timeout"),
    )
    def test_put(
        self,
        block,
        timeout,
        expected_timeout,
        event_serializer_mock,
        redis_mock,
        redis_stream_factory,
        event,
    ):
        kwargs = {}
        if block != SKIP:
            kwargs["block"] = block
        if timeout != SKIP:
            kwargs["timeout"] = timeout
        with mock.patch("eventscore.ext.redis.streams.Redis", redis_mock):
            stream = redis_stream_factory()
            stream.put(event, **kwargs)

        redis_mock.assert_has_calls(
            [
                mock.call.xadd(
                    name=str(event.type),
                    fields={"value": event_serializer_mock.encode.return_value},
                ),
            ]
        )
        event_serializer_mock.encode.assert_called_once_with(event)

    @pytest.mark.parametrize(
        "block,timeout,expected_timeout",
        (
            (SKIP, SKIP, 5000),
            (SKIP, 10, 10000),
            (False, SKIP, None),
            (False, 0, None),
            (True, SKIP, 5000),
            (True, 10, 10000),
        ),
        ids=(
            "blocking-by-default-default-timeout",
            "blocking-by-default-custom-timeout",
            "non-blocking-default-timeout",
            "non-blocking-custom-timeout",
            "blocking-default-timeout",
            "blocking-custom-timeout",
        ),
    )
    @pytest.mark.parametrize(
        "xreadgroup,expected_error",
        (
            ([], EmptyStreamError),
            ([tuple()], EmptyStreamError),
            ([(b"event", tuple())], EmptyStreamError),
            (
                [
                    (
                        b"event",
                        ((b"uid", {b"value": b"data"}, b"uid", {b"value": b"data"})),
                    )
                ],
                TooManyDataError,
            ),
            (
                [
                    (
                        b"event",
                        (
                            (
                                b"uid",
                                {b"value": b"data"},
                            ),
                        ),
                    )
                ],
                None,
            ),
        ),
        ids=(
            "empty-xreadgroup",
            "empty-events",
            "empty-messages-in-event",
            "too-many-messages-in-event",
            "valid-event",
        ),
    )
    @pytest.mark.parametrize(
        "xgroup_exists,instance_knows_xgroup_created,expect_xgroup_creation",
        (
            (False, False, True),
            (False, True, False),
            (True, False, True),
            (True, True, False),
        ),
    )
    def test_pop(
        self,
        block,
        timeout,
        expected_timeout,
        xreadgroup,
        expected_error,
        xgroup_exists,
        instance_knows_xgroup_created,
        expect_xgroup_creation,
        event_serializer_mock,
        redis_stream_factory,
        redis_mock,
    ):
        redis_mock.xreadgroup.return_value = xreadgroup
        if xgroup_exists:
            redis_mock.xgroup_create.side_effect = ResponseError
        kwargs = {}
        if block != SKIP:
            kwargs["block"] = block
        if timeout != SKIP:
            kwargs["timeout"] = timeout

        expected_redis_calls = []
        if expect_xgroup_creation:
            expected_redis_calls.append(
                mock.call.xgroup_create(
                    name="event",
                    groupname="group",
                    id="0",
                    mkstream=True,
                )
            )
        expected_redis_calls.append(
            mock.call.xreadgroup(
                groupname="group",
                consumername=str(os.getpid()),
                streams={"event": ">"},
                count=1,
                block=expected_timeout,
            )
        )
        if not expected_error:
            expected_redis_calls.append(mock.call.xack("event", "group", b"uid"))

        with mock.patch("eventscore.ext.redis.streams.Redis", redis_mock):
            stream = redis_stream_factory()

            getattr(stream, "_RedisStream__event_n_group_to_xgroup")[
                ("event", "group")
            ] = instance_knows_xgroup_created

            if expected_error is not None:
                with pytest.raises(expected_error):
                    stream.pop("event", "group", **kwargs)

                assert (
                    getattr(stream, "_RedisStream__event_n_group_to_xgroup")[
                        ("event", "group")
                    ]
                    is True
                )
                redis_mock.assert_has_calls(expected_redis_calls)
                event_serializer_mock.decode.assert_not_called()
            else:
                event = stream.pop("event", "group", **kwargs)

                assert event == event_serializer_mock.decode.return_value
                assert (
                    getattr(stream, "_RedisStream__event_n_group_to_xgroup")[
                        ("event", "group")
                    ]
                    is True
                )
                redis_mock.assert_has_calls(expected_redis_calls)
                event_serializer_mock.decode.assert_called_once_with(b"data")
