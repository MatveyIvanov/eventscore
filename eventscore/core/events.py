import uuid
from dataclasses import dataclass
from typing import TypeVar, Mapping, Any

TEvent = TypeVar("TEvent", bound=str)


@dataclass(frozen=True, slots=True)
class Event:
    uid: uuid.UUID
    type: TEvent
    created_at: str  # unix timestamp
    payload: Mapping[str, Any]
