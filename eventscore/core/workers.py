import logging
import multiprocessing as mp

from eventscore.core.abstract import ISpawnWorker
from eventscore.core.logging import logger as _logger
from eventscore.core.types import Worker


class SpawnMPWorker(ISpawnWorker):
    def __init__(self, logger: logging.Logger = _logger) -> None:
        """
        Construct spawn worker instance

        :param logger: Logger instance
        :type logger: logging.Logger
        """
        self.__logger = logger

    def __call__(self, worker: Worker) -> None:
        processes: list[mp.Process] = []
        for _ in range(worker.clones):
            process = mp.Process(target=worker.runner.run, daemon=True)
            processes.append(process)

        for process in processes:
            process.start()
            self.__logger.debug(f"Process {process.pid} has started.")
