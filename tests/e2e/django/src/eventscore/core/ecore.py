import importlib
import inspect
import logging
import os
import sys
from collections import defaultdict
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeAlias

from eventscore.core import pkg
from eventscore.core.abstract import (
    ConsumerFunc,
    ConsumerGroup,
    EventType,
    FunctionModulePath,
    IECore,
    IProcessPipeline,
    IProducer,
    ISpawnWorker,
    IStream,
    IStreamFactory,
    NumberOfClones,
)
from eventscore.core.exceptions import (
    AlreadySpawnedError,
    NotADirectoryError,
    NotAPackageError,
    PathError,
)
from eventscore.core.logging import logger as _logger
from eventscore.core.pipelines import Pipeline, PipelineItem, ProcessPipeline
from eventscore.core.producers import Producer
from eventscore.core.types import Event
from eventscore.core.workers import SpawnMPWorker, Worker
from eventscore.decorators import consumer as _consumer

FoundConsumerFunctions: TypeAlias = list[
    tuple[
        ConsumerFunc,
        EventType,
        ConsumerGroup,
        NumberOfClones,
        FunctionModulePath,
    ]
]


SKIPPED_CONTEXTS = {
    "makemigrations",
    "migrate",
}


def _skipping_predicate() -> bool:
    if any(context in sys.argv for context in SKIPPED_CONTEXTS):
        return True
    print(os.environ.get("RUN_MAIN", True), "*\n" * 10)
    if not os.environ.get("RUN_MAIN", True):
        return True
    return False


class ECore(IECore):
    def __init__(
        self,
        stream_factory: IStreamFactory,
        *,
        process_pipeline: IProcessPipeline | None = None,
        process_pipeline_type: type[IProcessPipeline] = ProcessPipeline,
        process_pipeline_init_kwargs: dict[str, Any] | None = None,
        spawn_worker: ISpawnWorker | None = None,
        spawn_worker_type: type[ISpawnWorker] = SpawnMPWorker,
        spawn_worker_init_kwargs: dict[str, Any] | None = None,
        producer: IProducer | None = None,
        producer_type: type[IProducer] = Producer,
        producer_init_kwargs: dict[str, Any] | None = None,
        logger: logging.Logger = _logger,
        skipping_predicate: Callable[[], bool] | None = _skipping_predicate,
    ) -> None:
        """
        ECore constructor

        :param stream_factory: Event stream factory
        :type stream_factory: IStreamFactory
        :param process_pipeline: Pipeline processor. Defaults to None
        :type process_pipeline: IProcessPipeline | None
        :param process_pipeline_type: Type of the pipeline processor.
            Defaults to ProcessPipeline.
            Param is ignored when process_pipeline is not None
        :type process_pipeline_type: type[IProcessPipeline]
        :param process_pipeline_init_kwargs: Initial kwargs for pipeline processor type.
            Defaults to None.
            Param is ignored when process_pipeline is not None
        :type process_pipeline_init_kwargs: dict[str, Any] | None
        :param spawn_worker: Worker spawner. Defaults to None
        :type spawn_worker: ISpawnWorker | None
        :param spawn_worker_type: Type of the worker spawner.
            Defaults to SpawnMPWorker.
            Param is ignored when spawn_worker is not None
        :type spawn_worker_type: type[ISpawnWorker]
        :param spawn_worker_init_kwargs: Initial kwargs for worker spawner type.
            Defaults to None.
            Param is ignored when spawn_worker is not None
        :type spawn_worker_init_kwargs: dict[str, Any] | None
        :param producer: Producer. Defaults to None
        :type producer: IProducer | None
        :param producer_type: Type of the producer.
            Defaults to Producer.
            Param is ignored when producer is not None
        :type producer_type: type[IProducer]
        :param producer_init_kwargs: Initial kwargs for producer type.
            Defaults to None.
            Param is ignored when producer is not None
        :type producer_init_kwargs: dict[str, Any] | None
        :param logger: Logger. Defaults to _logger
        :type logger: logging.Logger | None
        :param skipping_predicate: Predicate that ecore run in "dry" mode.
            Must return `True` to enable "dry"-run mode.
            As an example, default predicate returns True if python
            process is running a Django migration command.
        :type skipping_predicate: Callable[[], bool] | None
        """
        self.__stream_factory = stream_factory
        self.__stream: IStream | None = None
        self.__process_pipeline = process_pipeline
        self.__process_pipeline_type = process_pipeline_type
        self.__process_pipeline_init_kwargs = process_pipeline_init_kwargs
        self.__spawn_worker = spawn_worker
        self.__spawn_worker_type = spawn_worker_type
        self.__spawn_worker_init_kwargs = spawn_worker_init_kwargs
        self.__producer = producer
        self.__producer_type = producer_type
        self.__producer_init_kwargs = producer_init_kwargs
        self.__pipelines: dict[ConsumerGroup, Pipeline] = defaultdict(Pipeline)
        self.__workers: tuple[Worker, ...] | None = None
        self.__workers_spawned = False
        self.__logger = logger
        self.__skip = skipping_predicate() if skipping_predicate else False

        assert (
            self.__process_pipeline is not None
            or self.__process_pipeline_type is not None
        ), "Pipeline processor is required."
        assert (
            self.__spawn_worker is not None or self.__spawn_worker_type is not None
        ), "Worker spawner is required."
        # fmt:off
        # black and ruff conflict
        assert (
            self.__producer is not None or self.__producer_type is not None
        ), "Producer is required."
        # fmt:on

    @property
    def process_pipeline(self) -> IProcessPipeline:
        if self.__process_pipeline is None:
            kwargs = self.__process_pipeline_init_kwargs or {}
            kwargs.setdefault("logger", self.__logger)
            self.__process_pipeline = self.__process_pipeline_type(**kwargs)
        return self.__process_pipeline

    @property
    def spawn_worker(self) -> ISpawnWorker:
        if self.__spawn_worker is None:
            kwargs = self.__spawn_worker_init_kwargs or {}
            kwargs.setdefault("logger", self.__logger)
            self.__spawn_worker = self.__spawn_worker_type(**kwargs)
        return self.__spawn_worker

    @property
    def producer(self) -> IProducer:
        if self.__producer is None:
            kwargs = self.__producer_init_kwargs or {}
            kwargs.setdefault("ecore", self)
            kwargs.setdefault("logger", self.__logger)
            self.__producer = self.__producer_type(**kwargs)
        return self.__producer

    @property
    def stream_factory(self) -> IStreamFactory:
        return self.__stream_factory

    @property
    def stream(self) -> IStream:
        if self.__stream is None:
            self.__stream = self.stream_factory()
        return self.__stream

    def consumer(
        self,
        func: ConsumerFunc | None = None,
        *,
        event: EventType,
        group: ConsumerGroup,
        clones: int = 1,
    ) -> ConsumerFunc:
        return _consumer(func, ecore=self, event=event, group=group, clones=clones)

    def register_consumer(
        self,
        func: ConsumerFunc,
        event: EventType,
        group: ConsumerGroup,
        *,
        clones: int = 1,
        func_path: str | None = None,
    ) -> None:
        if self.__skip:
            self.__logger.warning(
                "Skipping consumer registration due to skipping predicate."
            )
            return
        if self.__workers_spawned:
            self.__logger.error("Consumer registration attempt after spawning.")
            raise AlreadySpawnedError
        # NOTE: consumer discovering returns unwrapped consumers,
        # but in the process also imports wrapped consumers.
        # While they are same in terms of consumer function,
        # they are still different in terms of python objects.
        # To avoid consumers duplication, we only add unwrapped versions
        # of found consumers, i.e. taking original function without decorator.
        # This is fine as far as consumer decorator only registers consumer
        # and not doing some runtime extra logic.
        func = getattr(func, "__wrapped__", func)

        self.__pipelines[group].items.add(
            PipelineItem(
                func=func,
                func_path=func_path
                or ((inspect.getsourcefile(func) or "") + ":" + func.__name__),
                event=event,
                group=group,
                clones=clones,
            )
        )
        self.__logger.info(
            "Consumer with "
            + f"func={func.__name__}, "
            + f"event={event}, "
            + f"group={group}, "
            + f"clones={clones} "
            + "is successfully registered."
        )

    def discover_consumers(self, *, root: str = "") -> None:
        if self.__skip:
            self.__logger.warning(
                "Skipping consumer discovering due to skipping predicate."
            )
            return
        if self.__workers_spawned:
            self.__logger.error("Consumer registration attempt after spawning.")
            raise AlreadySpawnedError

        abs_root = (Path(os.getcwd()) / root).resolve()
        if not abs_root.exists():
            raise PathError
        if not abs_root.is_dir():
            raise NotADirectoryError
        if not pkg.is_python_package(abs_root):
            raise NotAPackageError

        # Try to determine the package name from root.
        # We'll use its parent as the sys.path entry.
        pkg_root = abs_root
        # Example: /home/me/project/myapp/subpkg
        # Would sys.path.append /home/me/project and import myapp.subpkg.module
        # So, pkg="subpkg", sys_path_entry=pkg_root.parent

        # Guess the package name as the directory name, fallback to "." if not a package
        pkg_name = abs_root.name
        sys_path_entry = str(abs_root.parent)

        remove_sys_path = False
        if sys_path_entry not in sys.path:
            sys.path.append(sys_path_entry)
            remove_sys_path = True

        self.__logger.debug(
            f"Consumer discovering started for root={abs_root}, "
            + f"pkg_name={pkg_name}, "
            + f"sys_path_entry={sys_path_entry}"
        )

        found: FoundConsumerFunctions = []

        def is_consumer(obj: object) -> bool:
            return (
                inspect.isfunction(obj)
                and getattr(obj, "__is_consumer__", False)
                and hasattr(obj, "__consumer_event__")
                and hasattr(obj, "__consumer_group__")
                and hasattr(obj, "__consumer_clones__")
            )

        @contextmanager
        def temporary_sys_path_value(value: str, *, skip: bool) -> Iterator[None]:
            try:
                yield
            finally:
                if not skip:
                    sys.path.remove(value)

        with temporary_sys_path_value(sys_path_entry, skip=not remove_sys_path):
            for file_path in pkg.walk_files(pkg_root):
                if file_path.name == "__init__.py":
                    # Import package module: just pkg_name (e.g. 'myapp.subpkg')
                    modname = (
                        ".".join(
                            [pkg_name]
                            + list(file_path.parent.relative_to(pkg_root).parts)
                        )
                        if file_path.parent != pkg_root
                        else pkg_name
                    )
                else:
                    modname = pkg.module_name_from_path(file_path, pkg_root, pkg_name)

                self.__logger.debug(f"Discovering in module {modname} at {file_path}")

                try:
                    module = importlib.import_module(modname)
                except Exception as e:
                    self.__logger.warning(f"Skipping {modname} ({file_path}): {e!r}")
                    continue

                for _, func in inspect.getmembers(module, is_consumer):
                    found.append(
                        (
                            func,
                            func.__consumer_event__,
                            func.__consumer_group__,
                            func.__consumer_clones__,
                            f"{file_path}:{func.__name__}",
                        )
                    )
                    self.__logger.debug(f"Discovered consumer: {func} in {modname}")

        for func, event, group, clones, func_path in found:
            self.register_consumer(
                func,
                event,
                group,
                clones=clones,
                func_path=func_path,
            )

        self.__logger.debug(
            f"Consumer discovering ended. Found {len(found)} consumer functions."
        )

    def produce(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        if self.__skip:
            self.__logger.warning("Skipping event producing due to skipping predicate.")
            return
        self.producer.produce(event, block=block, timeout=timeout)

    def spawn_workers(self) -> None:
        if self.__skip:
            self.__logger.warning(
                "Skipping workers spawning due to skipping predicate."
            )
            return
        if self.__workers_spawned:
            self.__logger.warning("Spawn workers attempt when workers already spawned.")
            return
        if not self.__pipelines:
            self.__logger.warning("There is no registered consumers. Nothing to spawn.")
            return

        workers = self.__build_workers()
        for worker in workers:
            _ = self.spawn_worker(worker)
        self.__workers_spawned = True
        self.__logger.debug("Workers successfully spawned." + id(self).__str__())

    def __build_workers(self) -> tuple[Worker, ...]:
        if not self.__workers:
            self.__workers = tuple(
                self.process_pipeline(pipeline, self)
                for pipeline in self.__pipelines.values()
            )
            __newline = "\n"
            self.__logger.debug(
                "Built workers:\n\n"
                + f"{__newline.join(repr(worker) for worker in self.__workers)}\n"
            )

        return self.__workers
