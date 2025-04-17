import uuid

import pytest

from eventscore.core.types import Event


@pytest.mark.unit
class TestEventSerializer:
    @pytest.mark.parametrize(
        "event,expected_result",
        (
            (
                Event(
                    type="ping",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234",
                    payload={"field": "value"},
                ),
                b'{"type": "ping", "uid": "12345678-1234-5678-1234-567812345678", "ts": "1234", "payload": {"field": "value"}}',
            ),
            (
                Event(
                    type="pong",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="5678",
                    payload={"field": 1},
                ),
                b'{"type": "pong", "uid": "12345678-1234-5678-1234-567812345678", "ts": "5678", "payload": {"field": 1}}',
            ),
        ),
        ids=("str-value-payload", "int-value-payload"),
    )
    def test_encode(self, event, expected_result, event_serializer):
        assert event_serializer.encode(event) == expected_result

    @pytest.mark.parametrize(
        "event,expected_result",
        (
            (
                b'{"type": "ping", "uid": "12345678-1234-5678-1234-567812345678", "ts": "1234", "payload": {"field": "value"}}',
                Event(
                    type="ping",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234",
                    payload={"field": "value"},
                ),
            ),
            (
                b'{"type": "pong", "uid": "12345678-1234-5678-1234-567812345678", "ts": "5678", "payload": {"field": 1}}',
                Event(
                    type="pong",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="5678",
                    payload={"field": 1},
                ),
            ),
        ),
        ids=("str-value-payload", "int-value-payload"),
    )
    def test_decode(self, event, expected_result, event_serializer):
        assert event_serializer.decode(event) == expected_result


@pytest.mark.unit
class TestRedisEventSerializer:
    @pytest.mark.parametrize(
        "event,expected_result",
        (
            (
                Event(
                    type="ping",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234",
                    payload={"field": "value"},
                ),
                '{"type": "ping", "uid": "12345678-1234-5678-1234-567812345678", "ts": "1234", "payload": {"field": "value"}}',
            ),
            (
                Event(
                    type="pong",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="5678",
                    payload={"field": 1},
                ),
                '{"type": "pong", "uid": "12345678-1234-5678-1234-567812345678", "ts": "5678", "payload": {"field": 1}}',
            ),
        ),
        ids=("str-value-payload", "int-value-payload"),
    )
    def test_encode(self, event, expected_result, redis_event_serializer):
        assert redis_event_serializer.encode(event) == expected_result

    @pytest.mark.parametrize(
        "event,expected_result",
        (
            (
                b'{"type": "ping", "uid": "12345678-1234-5678-1234-567812345678", "ts": "1234", "payload": {"field": "value"}}',
                Event(
                    type="ping",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234",
                    payload={"field": "value"},
                ),
            ),
            (
                b'{"type": "pong", "uid": "12345678-1234-5678-1234-567812345678", "ts": "5678", "payload": {"field": 1}}',
                Event(
                    type="pong",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="5678",
                    payload={"field": 1},
                ),
            ),
        ),
        ids=("str-value-payload", "int-value-payload"),
    )
    def test_decode(self, event, expected_result, redis_event_serializer):
        assert redis_event_serializer.decode(event) == expected_result
