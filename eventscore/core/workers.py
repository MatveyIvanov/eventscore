import uuid
from dataclasses import dataclass

from eventscore.core.abstract import IObserver, ISpawnWorker


@dataclass(frozen=True, slots=True)
class Worker:
    uid: uuid.UUID
    name: str
    clones: int
    observer: IObserver


class SpawnMPWorker(ISpawnWorker):
    def __call__(self, worker: Worker, observer: IObserver) -> None:
        pass
