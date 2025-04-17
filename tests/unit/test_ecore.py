from collections import defaultdict
from unittest import mock

import pytest

from eventscore.core.exceptions import AlreadySpawnedError
from eventscore.core.types import Event, Pipeline, PipelineItem
from tests.unit.conftest import SELF, SKIP


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
        "property_name,property_specific_args",
        (("process_pipeline", None), ("spawn_worker", None), ("producer", (SELF,))),
        ids=("process-pipeline", "spawn-worker", "producer"),
    )
    def test_properties(
        self,
        property_name,
        property_specific_args,
        instance,
        expect_init,
        type,
        init_kwargs,
        expected_init_kwargs,
        ecore_factory,
    ):
        if instance in (None, SKIP) and type is None:
            pytest.skip("Skipping expected error. Error covered in another test.")

        kwargs = {
            property_name: instance,
            f"{property_name}_type": type,
            f"{property_name}_init_kwargs": init_kwargs,
        }
        if type in (None, SKIP):
            # mock default value
            type = mock.Mock()

        type.reset_mock()

        ecore = ecore_factory(
            kwdefaults_overrides={f"{property_name}_type": type},
            **kwargs,
        )
        if property_specific_args:
            property_specific_args = tuple(
                arg if arg != SELF else ecore for arg in property_specific_args
            )

        if expect_init:
            assert getattr(ecore, property_name) == type.return_value
            type.assert_called_once_with(
                *(property_specific_args or tuple()),
                **expected_init_kwargs,
            )
            # second call, still called once
            assert getattr(ecore, property_name) == type.return_value
            type.assert_called_once_with(
                *(property_specific_args or tuple()),
                **expected_init_kwargs,
            )
        else:
            assert getattr(ecore, property_name) == instance
            type.assert_not_called()
            # second call, still not called
            assert getattr(ecore, property_name) == instance
            type.assert_not_called()

    def test_stream(self, stream_mock, ecore_factory):
        ecore = ecore_factory(stream=stream_mock)

        assert ecore.stream == stream_mock

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
    @pytest.mark.parametrize("func", (mock.Mock(),), ids=("func",))
    @pytest.mark.parametrize("event", ("event",), ids=("event",))
    @pytest.mark.parametrize("group", ("group",), ids=("group",))
    @pytest.mark.parametrize("clones", (SKIP, 2), ids=("default-clones", "two-clones"))
    def test_register_consumer(
        self,
        already_spawned,
        expected_error,
        func,
        event,
        group,
        clones,
        ecore_factory,
    ):
        func.__name__ = "name"
        kwargs = dict(
            func=func,
            event=event,
            group=group,
        )
        if clones != SKIP:
            kwargs["clones"] = clones

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
                                func=func,
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
                    items={PipelineItem(func=mock.Mock(), event="event", group="group")}
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
