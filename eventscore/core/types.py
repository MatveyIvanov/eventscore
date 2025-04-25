from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from time import time
from typing import Any, TypeAlias, TypedDict

# FIXME: Duplicating definitions from abstract for now,
# FIXME: to evade circular import problem
EventType: TypeAlias = str | StrEnum | IntEnum

EncodableT = str | int | bytes

DEFAULT_CONSUMER_GROUP = "default"


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
    payload: dict[str, EncodableT]


@dataclass(frozen=True, slots=True)
class Event:
    """
    Event class

    :param type: type of the event
    :type type: EventType
    :param uid: unique id of the event. Defaults to random uuid4
    :type uid: uuid.UUID
    :param ts: timestamp of the event. Defaults to current timestamp
    :type ts: str
    :param payload: payload of the event. Defaults to empty dict
    :type payload: dict[str, EncodableT]
    """

    type: EventType
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    ts: str = field(default_factory=lambda: str(time()))
    payload: dict[str, EncodableT] = field(default_factory=dict)  # pyright:ignore[reportUnknownVariableType]  # noqa:E501

    def asdict(self) -> EventDict:
        """
        Custom asdict method for result to be encodable

        :return: Dictionary representation of the event
        :rtype: EventDict
        """
        return {
            "type": str(self.type),
            "uid": str(self.uid),
            "ts": self.ts,
            "payload": self.payload,
        }

    @classmethod
    def fromdict(cls, obj: EventDict) -> Event:
        """
        Classmethod for event construction from encodable dictionary

        :param obj: Dictionary representation of the event
        :type obj: EventDict
        :return: Event object
        :rtype: Event
        """
        return Event(
            type=obj["type"],
            uid=uuid.UUID(obj["uid"]),
            ts=obj["ts"],
            payload=obj["payload"],
        )


# FIXME: Duplicating definitions from abstract for now,
# FIXME: to evade circular import problem
# Type alias for user-defined consumer functions/other callables
ConsumerFunc: TypeAlias = Callable[[Event], Any]
# Type alias for user-defined consumer groups
ConsumerGroup: TypeAlias = str | StrEnum | IntEnum


@dataclass(frozen=True, slots=True)
class PipelineItem:
    """
    Pipeline item class

    :param func: consumer function
    :type func: ConsumerFunc
    :param event: event type
    :type event: EventType
    :param group: consumer group. Defaults to DEFAULT_CONSUMER_GROUP
    :type group: ConsumerGroup
    :param clones: number of clones. Defaults to 1
    :type clones: int
    """

    func: ConsumerFunc
    event: EventType
    group: ConsumerGroup = DEFAULT_CONSUMER_GROUP
    clones: int = 1

    def __eq__(self, other: PipelineItem) -> bool:  # type:ignore[override]
        """
        Equality operator for pipeline items.

        :param other: other pipeline item
        :type other: PipelineItem
        :return: True if the two pipeline items are equal, False otherwise
        :rtype: bool
        """
        return (
            self.func == other.func
            and self.event == other.event
            and self.group == other.group
        )


@dataclass(frozen=True, slots=True)
class Pipeline:
    """
    Pipeline class

    :param uid: unique id of the pipeline. Defaults to random uuid4
    :type uid: uuid.UUID
    :param items: set of pipeline items. Defaults to empty set
    :type items: set[PipelineItem]
    """

    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    items: set[PipelineItem] = field(default_factory=set)  # pyright:ignore[reportUnknownVariableType]  # noqa:E501


@dataclass(frozen=True, slots=True)
class Worker:
    """
    Worker class

    :param name: name of the worker
    :type name: str
    :param runner: runner for the worker
    :type runner: Any
    :param clones: number of clones. Defaults to 1
    :type clones: int
    :param uid: unique id of the worker. Defaults to random uuid4
    :type uid: uuid.UUID
    """

    name: str
    runner: Any  # FIXME: type annotation causes circular import problem
    clones: int = 1
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
