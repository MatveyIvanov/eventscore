from unittest import mock

import pytest

from eventscore.core.exceptions import EmptyStreamError, TooManyDataError
from eventscore.ext.redis.streams import RedisStream
from tests.unit.conftest import SKIP


@pytest.mark.unit
class TestRedisStream:
    @pytest.mark.parametrize(
        "host,port,db,redis_init_kwargs,expected_redis_init_kwargs",
        (
            (
                "redis",
                6379,
                0,
                SKIP,
                {"host": "redis", "port": 6379, "db": 0},
            ),
            (
                "redis",
                6379,
                0,
                None,
                {"host": "redis", "port": 6379, "db": 0},
            ),
            (
                "redis",
                6379,
                0,
                {},
                {"host": "redis", "port": 6379, "db": 0},
            ),
            (
                "redis",
                6379,
                0,
                {"password": "password"},
                {"host": "redis", "port": 6379, "db": 0, "password": "password"},
            ),
            (
                "redis",
                6379,
                0,
                {"password": "password", "host": "newhost"},
                {"host": "redis", "port": 6379, "db": 0, "password": "password"},
            ),
        ),
        ids=(
            "default-init-kwargs",
            "none-init-kwargs",
            "empty-init-kwargs",
            "filled-init-kwargs",
            "override-attempt-init_kwargs",
        ),
    )
    def test_init(
        self,
        host,
        port,
        db,
        redis_init_kwargs,
        expected_redis_init_kwargs,
        redis_event_serializer,
        redis_mock,
    ):
        kwargs = {}
        if redis_init_kwargs != SKIP:
            kwargs["redis_init_kwargs"] = redis_init_kwargs
        with mock.patch("eventscore.ext.redis.streams.redis", redis_mock):
            RedisStream(host, port, db, redis_event_serializer, **kwargs)

        redis_mock.Redis.assert_called_once_with(**expected_redis_init_kwargs)

    @pytest.mark.parametrize("block", (False, True), ids=("non-blocking", "blocking"))
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
        kwargs = {"block": block}
        if timeout != SKIP:
            kwargs["timeout"] = timeout
        with mock.patch("eventscore.ext.redis.streams.redis", redis_mock):
            stream = redis_stream_factory()
            stream.put(event, **kwargs)

        redis_mock.assert_has_calls(
            [
                mock.call.Redis(host="redis", port=6379, db=0),
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
            (False, SKIP, None),
            (False, 0, None),
            (True, SKIP, 5000),
            (True, 10, 10000),
        ),
        ids=(
            "non-blocking-default-timeout",
            "non-blocking-custom-timeout",
            "blocking-default-timeout",
            "blocking-custom-timeout",
        ),
    )
    @pytest.mark.parametrize(
        "xread,expected_error",
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
            "empty-xread",
            "empty-events",
            "empty-messages-in-event",
            "too-many-messages-in-event",
            "valid-event",
        ),
    )
    def test_pop(
        self,
        block,
        timeout,
        expected_timeout,
        xread,
        expected_error,
        event_serializer_mock,
        redis_stream_factory,
        redis_mock,
    ):
        redis_mock.xread.return_value = xread
        kwargs = {"block": block}
        if timeout != SKIP:
            kwargs["timeout"] = timeout

        with mock.patch("eventscore.ext.redis.streams.redis", redis_mock):
            stream = redis_stream_factory()

            assert getattr(stream, "_RedisStream__event_to_latest_id")["event"] == "0"

            if expected_error is not None:
                with pytest.raises(expected_error):
                    stream.pop("event", **kwargs)

                assert (
                    getattr(stream, "_RedisStream__event_to_latest_id")["event"] == "0"
                )
                redis_mock.assert_has_calls(
                    [
                        mock.call.Redis(host="redis", port=6379, db=0),
                        mock.call.xread(
                            streams={"event": "0"},
                            count=1,
                            block=expected_timeout,
                        ),
                    ]
                )
                event_serializer_mock.decode.assert_not_called()
            else:
                event = stream.pop("event", **kwargs)

                assert event == event_serializer_mock.decode.return_value
                assert (
                    getattr(stream, "_RedisStream__event_to_latest_id")["event"]
                    == "uid"
                )
                redis_mock.assert_has_calls(
                    [
                        mock.call.Redis(host="redis", port=6379, db=0),
                        mock.call.xread(
                            streams={"event": "0"},
                            count=1,
                            block=expected_timeout,
                        ),
                    ]
                )
                event_serializer_mock.decode.assert_called_once_with(b"data")
