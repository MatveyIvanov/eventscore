import multiprocessing as mp

from eventscore.core.abstract import ISpawnWorker
from eventscore.core.types import Worker


class SpawnMPWorker(ISpawnWorker):
    def __call__(self, worker: Worker) -> None:
        processes = []
        for _ in range(worker.clones):
            process = mp.Process(target=worker.runner.run, daemon=True)
            processes.append(process)

        for process in processes:
            process.start()
