import functools
import inspect
from collections import defaultdict
from unittest import mock

import pytest

from eventscore.core.exceptions import AlreadySpawnedError
from eventscore.core.logging import logger as _logger
from eventscore.core.types import Event, Pipeline, PipelineItem
from tests.unit.conftest import SKIP


def consumer_decorator(func):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def consumer_func():
    pass


@consumer_decorator
def wrapped_consumer_func():
    pass


@pytest.mark.unit
class TestECore:
    @pytest.mark.parametrize(
        "kwargs",
        (
            {"process_pipeline": None, "process_pipeline_type": None},
            {"process_pipeline": SKIP, "process_pipeline_type": None},
            {"spawn_worker": None, "spawn_worker_type": None},
            {"spawn_worker": SKIP, "spawn_worker_type": None},
            {"producer": None, "producer_type": None},
            {"producer": SKIP, "producer_type": None},
        ),
        ids=(
            "explicit-none-process-pipeline",
            "implicit-none-via-process-pipeline-type-none",
            "explicit-none-spawn-worker",
            "implicit-none-via-spawn-worker-type-none",
            "explicit-none-producer",
            "implicit-none-via-producer-type-none",
        ),
    )
    def test_init(self, kwargs, ecore_factory):
        with pytest.raises(AssertionError):
            ecore_factory(**kwargs)

    @pytest.mark.parametrize(
        "type,init_kwargs,expected_init_kwargs",
        (
            (SKIP, SKIP, {}),
            (SKIP, None, {}),
            (SKIP, {}, {}),
            (SKIP, {"field": "value"}, {"field": "value"}),
            (None, SKIP, {}),
            (None, None, {}),
            (None, {}, {}),
            (None, {"field": "value"}, {"field": "value"}),
            (mock.Mock(), SKIP, {}),
            (mock.Mock(), None, {}),
            (mock.Mock(), {}, {}),
            (mock.Mock(), {"field": "value"}, {"field": "value"}),
        ),
        ids=(
            "default-type-w-default-kwargs",
            "default-type-w-none-kwargs",
            "default-type-w-empty-kwargs",
            "default-type-w-filled-kwargs",
            "none-type-w-default-kwargs",
            "none-type-w-none-kwargs",
            "none-type-w-empty-kwargs",
            "none-type-w-filled-kwargs",
            "valid-type-w-default-kwargs",
            "valid-type-w-none-kwargs",
            "valid-type-w-empty-kwargs",
            "valid-type-w-filled-kwargs",
        ),
    )
    @pytest.mark.parametrize(
        "instance,expect_init",
        (
            (SKIP, True),
            (None, True),
            (mock.Mock(), False),
        ),
        ids=(
            "default-instance",
            "none-instance",
            "valid-instance",
        ),
    )
    @pytest.mark.parametrize(
        "property_name",
        (
            "process_pipeline",
            "spawn_worker",
            "producer",
        ),
        ids=(
            "process-pipeline",
            "spawn-worker",
            "producer",
        ),
    )
    @pytest.mark.parametrize(
        "logger",
        (SKIP, mock.Mock()),
        ids=("default-logger", "custom-logger"),
    )
    def test_properties(
        self,
        logger,
        property_name,
        instance,
        expect_init,
        type,
        init_kwargs,
        expected_init_kwargs,
        ecore_factory,
    ):
        if instance in (None, SKIP) and type is None:
            pytest.skip("Skipping expected error. Error covered in another test.")

        # IMHO, this is a bug in pytest
        # Keeping state between parametrize params is not what I expect
        if isinstance(init_kwargs, dict):
            init_kwargs.pop("logger", None)
            init_kwargs.pop("ecore", None)

        kwargs = {
            property_name: instance,
            f"{property_name}_type": type,
            f"{property_name}_init_kwargs": init_kwargs,
        }
        if logger != SKIP:
            kwargs["logger"] = logger
        if type in (None, SKIP):
            # mock default value
            type = mock.Mock()

        ecore = ecore_factory(
            kwdefaults_overrides={f"{property_name}_type": type},
            **kwargs,
        )

        expected_init_kwargs["logger"] = logger or _logger
        if property_name in ("producer",):
            expected_init_kwargs["ecore"] = ecore
        else:
            # Same bug in pytest
            expected_init_kwargs.pop("ecore", None)

        for obj in (type, instance, logger):
            if isinstance(obj, mock.Mock):
                obj.reset_mock()

        if expect_init:
            assert getattr(ecore, property_name) == type.return_value
            type.assert_called_once_with(**expected_init_kwargs)
            # second call, still called once
            assert getattr(ecore, property_name) == type.return_value
            type.assert_called_once_with(**expected_init_kwargs)
        else:
            assert getattr(ecore, property_name) == instance
            type.assert_not_called()
            # second call, still not called
            assert getattr(ecore, property_name) == instance
            type.assert_not_called()

    def test_stream_factory(self, stream_factory_mock, ecore_factory):
        ecore = ecore_factory(stream_factory=stream_factory_mock)

        assert ecore.stream_factory == stream_factory_mock

    @pytest.mark.parametrize("func", (mock.Mock(), None), ids=("func", "no-func"))
    @pytest.mark.parametrize("event", ("event",), ids=("event",))
    @pytest.mark.parametrize("group", ("group",), ids=("group",))
    @pytest.mark.parametrize("clones", (1,), ids=("single",))
    def test_consumer(
        self,
        func,
        event,
        group,
        clones,
        consumer_decorator_mock,
        ecore_factory,
        mocker,
    ):
        mocker.patch("eventscore.core.ecore._consumer", consumer_decorator_mock)
        consumer_decorator_mock.return_value = func

        ecore = ecore_factory()

        result = ecore.consumer(func, event=event, group=group, clones=clones)

        assert result == func
        consumer_decorator_mock.assert_called_once_with(
            func,
            ecore=ecore,
            event=event,
            group=group,
            clones=clones,
        )

    @pytest.mark.parametrize(
        "already_spawned,expected_error",
        ((False, None), (True, AlreadySpawnedError)),
        ids=("already-spawned", "not-spawned"),
    )
    @pytest.mark.parametrize(
        "func,expected_func",
        (
            (consumer_func, consumer_func),
            (wrapped_consumer_func, wrapped_consumer_func.__wrapped__),
        ),
        ids=("func", "wrapped_func"),
    )
    @pytest.mark.parametrize("event", ("event",), ids=("event",))
    @pytest.mark.parametrize("group", ("group",), ids=("group",))
    @pytest.mark.parametrize("clones", (SKIP, 2), ids=("default-clones", "two-clones"))
    @pytest.mark.parametrize("func_path", (SKIP, None, "", "path"))
    def test_register_consumer(
        self,
        already_spawned,
        expected_error,
        func,
        expected_func,
        event,
        group,
        clones,
        func_path,
        ecore_factory,
    ):
        expected_func_path = (
            func_path or inspect.getsourcefile(func) + ":" + func.__name__
        )
        kwargs = dict(
            func=func,
            event=event,
            group=group,
        )
        if clones != SKIP:
            kwargs["clones"] = clones
        if func_path != SKIP:
            kwargs["func_path"] = func_path

        ecore = ecore_factory()
        if already_spawned:
            setattr(ecore, "_ECore__workers_spawned", True)

        if expected_error is not None:
            with pytest.raises(expected_error):
                ecore.register_consumer(**kwargs)

            pipelines = getattr(ecore, "_ECore__pipelines")
            assert pipelines == defaultdict(
                Pipeline,
                {
                    group: Pipeline(
                        uid=pipelines[group].uid,
                        items=set(),
                    )
                },
            )
        else:
            ecore.register_consumer(**kwargs)

            pipelines = getattr(ecore, "_ECore__pipelines")
            assert pipelines == defaultdict(
                Pipeline,
                {
                    group: Pipeline(
                        uid=pipelines[group].uid,
                        items={
                            PipelineItem(
                                func=expected_func,
                                func_path=expected_func_path,
                                event=event,
                                group=group,
                                clones=clones if clones != SKIP else 1,
                            )
                        },
                    )
                },
            )

    def test_discover_consumers(self):
        # TODO: need tests, and some refactoring afterwards
        pass

    @pytest.mark.parametrize("event", (Event(type="event"),), ids=("event",))
    @pytest.mark.parametrize("block", (False, True), ids=("non-blocking", "blocking"))
    @pytest.mark.parametrize(
        "timeout",
        (SKIP, 0),
        ids=("default-timeout", "zero-timeout"),
    )
    def test_produce(self, event, block, timeout, producer_mock, ecore_factory):
        kwargs = dict(event=event, block=block)
        if timeout != SKIP:
            kwargs["timeout"] = timeout

        ecore = ecore_factory()

        result = ecore.produce(event, block=block, timeout=timeout)

        assert result is None
        producer_mock.produce.assert_called_once_with(
            event,
            block=block,
            timeout=timeout,
        )

    @pytest.mark.parametrize(
        "already_spawned",
        (False, True),
        ids=("not-spawned", "already-spawned"),
    )
    @pytest.mark.parametrize(
        "pipelines",
        (
            {},
            {
                "group": Pipeline(
                    items={
                        PipelineItem(
                            func=mock.Mock(),
                            func_path="path",
                            event="event",
                            group="group",
                        )
                    }
                )
            },
        ),
        ids=("empty-pipelines", "non-empty-pipelines"),
    )
    def test_spawn_workers(
        self,
        already_spawned,
        pipelines,
        spawn_worker_mock,
        process_pipeline_mock,
        ecore_factory,
    ):
        ecore = ecore_factory()
        setattr(ecore, "_ECore__workers_spawned", already_spawned)
        setattr(ecore, "_ECore__pipelines", pipelines)
        expected_workers = tuple(
            [process_pipeline_mock.return_value] * len(pipelines.values())
        )

        result = ecore.spawn_workers()

        assert result is None
        if already_spawned or not pipelines:
            assert getattr(ecore, "_ECore__workers_spawned") is already_spawned
            assert getattr(ecore, "_ECore__workers") is None
            process_pipeline_mock.assert_not_called()
            spawn_worker_mock.assert_not_called()
        else:
            assert getattr(ecore, "_ECore__workers_spawned") is True
            assert getattr(ecore, "_ECore__workers") == expected_workers
            process_pipeline_mock.assert_has_calls(
                [mock.call(pipeline, ecore) for pipeline in pipelines.values()]
            )
            spawn_worker_mock.assert_has_calls(
                [mock.call(worker) for worker in expected_workers]
            )
