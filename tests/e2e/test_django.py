import json
import time
from uuid import UUID

import pytest
import requests

from eventscore.core.types import Event

URL = "http://localhost:8000/api/v0/ping/"


@pytest.mark.e2e
class TestDjangoApplication:
    @pytest.mark.parametrize("count", (0, 1, 2, 5, 10))
    @pytest.mark.parametrize(
        "payload",
        (
            None,
            {},
            {"field": "value"},
            {"outer": {"inner": "value", "empty": {}}, "empty": None},
        ),
    )
    def test_ping(self, count, payload, cursor):
        for _ in range(count):
            response = requests.post(
                URL,
                json={"event": "ping", "payload": payload},
            )
            assert response.status_code == 200
            assert response.json() == {"detail": "OK"}

        time.sleep(0.1)

        events = cursor.execute("SELECT * FROM events_eventmodel").fetchall()
        logs = cursor.execute("SELECT * FROM events_eventlog").fetchall()

        assert len(events) == len(logs)
        assert len(events) == count
        assert len(logs) == count
        for (_, uid, type, ts, _payload), (_, log, _) in zip(
            # sorted by ts, as we do not guarantee consuming order
            sorted(events, key=lambda event: event[3]),
            # sorted by dt, as we do not guarantee consuming order
            sorted(logs, key=lambda log: log[2]),
        ):
            assert uid is not None
            assert type == "ping"
            assert ts is not None
            assert _payload == json.dumps(payload)
            assert log == repr(
                Event(
                    type=type,
                    uid=UUID(uid),
                    ts=ts,
                    payload=json.loads(_payload),
                )
            )
