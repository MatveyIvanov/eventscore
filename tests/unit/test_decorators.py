import pytest

from eventscore.decorators import consumer
from tests.unit.conftest import SKIP


@pytest.mark.unit
@pytest.mark.parametrize(
    "func",
    (
        SKIP,
        None,
        "consumer_func_mock",
    ),
)
def test_consumer_decorator(func, ecore_mock, consumer_func_mock):
    kwargs = dict(
        ecore=ecore_mock,
        event="event",
        group="group",
        clones=1,
    )
    if func != SKIP:
        kwargs["func"] = consumer_func_mock if func else func

    decorated = consumer(**kwargs)
    if not func:
        # case when func is None (e.g. no parentheses)
        decorated = decorated(consumer_func_mock)

    assert consumer_func_mock.__is_consumer__ is True
    assert consumer_func_mock.__consumer_event__ == "event"
    assert consumer_func_mock.__consumer_group__ == "group"
    assert consumer_func_mock.__consumer_clones__ == 1
    ecore_mock.register_consumer.assert_called_once_with(
        consumer_func_mock,
        "event",
        "group",
        clones=1,
    )

    args, kwargs = (1,), {"field": "value"}
    result = decorated(*args, **kwargs)

    assert result == consumer_func_mock.return_value
    consumer_func_mock.assert_called_once_with(*args, **kwargs)
