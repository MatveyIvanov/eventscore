from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from time import time
from typing import Any, Callable, Mapping, Set, TypeAlias, TypedDict, Union

# FIXME: Duplicating definitions from abstract for now,
# FIXME: to evade circular import problem
EventType: TypeAlias = Union[str, StrEnum, IntEnum]

EncodableT = Union[str, int, bytes]


class DeliverySemantic(IntEnum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class EventStatus(IntEnum):
    PENDING = 0
    SENT = 1
    FAILED = 2


class EventDict(TypedDict):
    type: str
    uid: str
    ts: str
    payload: Mapping[str, EncodableT]


@dataclass(frozen=True, slots=True)
class Event:
    type: EventType
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    ts: str = field(default_factory=lambda: str(time()))  # unix timestamp
    payload: Mapping[str, EncodableT] = field(default_factory=dict)

    def asdict(self) -> EventDict:
        return {
            "type": str(self.type),
            "uid": str(self.uid),
            "ts": self.ts,
            "payload": self.payload,
        }

    @classmethod
    def fromdict(cls, obj: EventDict) -> Event:
        return Event(
            type=obj["type"],
            uid=uuid.UUID(obj["uid"]),
            ts=obj["ts"],
            payload=obj["payload"],
        )


# FIXME: Duplicating definitions from abstract for now,
# FIXME: to evade circular import problem
ConsumerFunc: TypeAlias = Callable[[Event], Any]
ConsumerGroup: TypeAlias = Union[str, StrEnum, IntEnum]


@dataclass(frozen=True, slots=True)
class PipelineItem:
    func: ConsumerFunc
    event: EventType
    group: ConsumerGroup
    clones: int = 1

    def __eq__(self, other: PipelineItem) -> bool:  # type:ignore[override]
        return (
            self.func == other.func
            and self.event == other.event
            and self.group == other.group
        )


@dataclass(frozen=True, slots=True)
class Pipeline:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    items: Set[PipelineItem] = field(default_factory=set)


@dataclass(frozen=True, slots=True)
class Worker:
    uid: uuid.UUID
    name: str
    clones: int
    runner: Any  # FIXME: type annotation causes circular import problem
