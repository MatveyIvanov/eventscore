import uuid
from time import time

import pytest

from eventscore.core.types import Event, Pipeline, PipelineItem, Worker


@pytest.mark.unit
class TestEvent:
    @property
    def _full_init(self):
        return {
            "type": "event",
            "uid": uuid.uuid4(),
            "ts": str(time()),
            "payload": dict(),
        }

    @pytest.mark.parametrize(
        "missing_field,expect_type,expect_error",
        (
            ("type", None, TypeError),
            ("uid", uuid.UUID, None),
            ("ts", str, None),
            ("payload", dict, None),
        ),
        ids=(
            "missing-type",
            "missing-uid",
            "missing-ts",
            "missing-payload",
        ),
    )
    def test_defaults(self, missing_field, expect_type, expect_error):
        init = self._full_init
        del init[missing_field]

        if expect_error:
            with pytest.raises(expect_error):
                Event(**init)

        else:
            event = Event(**init)

            assert isinstance(getattr(event, missing_field), expect_type)

    @pytest.mark.parametrize(
        "event,expected_dict",
        (
            (
                Event(
                    type="event",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234567890",
                    payload=dict(),
                ),
                {
                    "type": "event",
                    "uid": "12345678-1234-5678-1234-567812345678",
                    "ts": "1234567890",
                    "payload": dict(),
                },
            ),
            (
                Event(
                    type="event",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234567890",
                    payload={
                        "field": "value",
                    },
                ),
                {
                    "type": "event",
                    "uid": "12345678-1234-5678-1234-567812345678",
                    "ts": "1234567890",
                    "payload": {
                        "field": "value",
                    },
                },
            ),
        ),
        ids=(
            "empty-payload-event",
            "filled-payload-event",
        ),
    )
    def test_asdict(self, event, expected_dict):
        assert event.asdict() == expected_dict

    @pytest.mark.parametrize(
        "dct,expected_event",
        (
            (
                {
                    "type": "event",
                    "uid": "12345678-1234-5678-1234-567812345678",
                    "ts": "1234567890",
                    "payload": dict(),
                },
                Event(
                    type="event",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234567890",
                    payload=dict(),
                ),
            ),
            (
                {
                    "type": "event",
                    "uid": "12345678-1234-5678-1234-567812345678",
                    "ts": "1234567890",
                    "payload": {
                        "field": "value",
                    },
                },
                Event(
                    type="event",
                    uid=uuid.UUID("12345678-1234-5678-1234-567812345678"),
                    ts="1234567890",
                    payload={
                        "field": "value",
                    },
                ),
            ),
        ),
        ids=(
            "empty-payload-event",
            "filled-payload-event",
        ),
    )
    def test_fromdict(self, dct, expected_event):
        assert Event.fromdict(dct) == expected_event


@pytest.mark.unit
class TestPipelineItem:
    @property
    def _full_init(self):
        return {
            "func": int,
            "func_path": "path",
            "event": "event",
            "group": "group",
            "clones": 1,
        }

    @pytest.mark.parametrize(
        "missing_field,expect_type,expect_error",
        (
            ("func", None, TypeError),
            ("func_path", None, TypeError),
            ("event", None, TypeError),
            ("group", str, None),
            ("clones", int, None),
        ),
        ids=(
            "missing-func",
            "missing-func-path",
            "missing-event",
            "missing-group",
            "missing-clones",
        ),
    )
    def test_defaults(self, missing_field, expect_type, expect_error):
        init = self._full_init
        del init[missing_field]

        if expect_error:
            with pytest.raises(expect_error):
                PipelineItem(**init)

        else:
            item = PipelineItem(**init)

            assert isinstance(getattr(item, missing_field), expect_type)

    @pytest.mark.parametrize(
        "item1,item2,expect_equal",
        (
            (
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=1,
                ),
                True,
            ),
            (
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=2,
                ),
                True,
            ),
            (
                PipelineItem(
                    func=float,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group",
                    clones=1,
                ),
                False,
            ),
            (
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event1",
                    group="group",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event2",
                    group="group",
                    clones=1,
                ),
                False,
            ),
            (
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group1",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path",
                    event="event",
                    group="group2",
                    clones=1,
                ),
                False,
            ),
            (
                PipelineItem(
                    func=int,
                    func_path="path1",
                    event="event",
                    group="group",
                    clones=1,
                ),
                PipelineItem(
                    func=int,
                    func_path="path2",
                    event="event",
                    group="group",
                    clones=1,
                ),
                False,
            ),
        ),
        ids=(
            "equal",
            "equal-with-clones-diff",
            "not-equal-func-diff",
            "not-equal-event-diff",
            "not-equal-group-diff",
            "not-equal-func-path-diff",
        ),
    )
    def test_eq(self, item1, item2, expect_equal):
        assert (item1 == item2) is expect_equal

    @pytest.mark.parametrize("func", (int,), ids=("func",))
    @pytest.mark.parametrize("func_path", ("path",), ids=("path",))
    @pytest.mark.parametrize("event", ("event",), ids=("event",))
    @pytest.mark.parametrize("group", ("group",), ids=("group",))
    @pytest.mark.parametrize("clones", (1, 2), ids=("one", "two"))
    def test_hash(self, func, func_path, event, group, clones):
        assert hash(
            PipelineItem(
                func=func,
                func_path=func_path,
                event=event,
                group=group,
                clones=clones,
            )
        ) == hash(
            (
                func,
                func_path,
                event,
                group,
            )
        )


@pytest.mark.unit
class TestPipeline:
    @property
    def _full_init(self):
        return {
            "uid": uuid.uuid4(),
            "items": set(),
        }

    @pytest.mark.parametrize(
        "missing_field,expect_type,expect_error",
        (
            ("uid", uuid.UUID, None),
            ("items", set, None),
        ),
        ids=(
            "missing-uid",
            "missing-items",
        ),
    )
    def test_defaults(self, missing_field, expect_type, expect_error):
        init = self._full_init
        del init[missing_field]

        if expect_error:
            with pytest.raises(expect_error):
                Pipeline(**init)

        else:
            pipeline = Pipeline(**init)

            assert isinstance(getattr(pipeline, missing_field), expect_type)


@pytest.mark.unit
class TestWorker:
    @property
    def _full_init(self):
        return {
            "name": "name",
            "runner": None,
            "clones": 1,
            "uid": uuid.uuid4(),
        }

    @pytest.mark.parametrize(
        "missing_field,expect_type,expect_error",
        (
            ("name", None, TypeError),
            ("runner", None, TypeError),
            ("clones", int, None),
            ("uid", uuid.UUID, None),
        ),
        ids=(
            "missing-name",
            "missing-runner",
            "missing-clones",
            "missing-uid",
        ),
    )
    def test_defaults(self, missing_field, expect_type, expect_error):
        init = self._full_init
        del init[missing_field]

        if expect_error:
            with pytest.raises(expect_error):
                Worker(**init)

        else:
            worker = Worker(**init)

            assert isinstance(getattr(worker, missing_field), expect_type)
