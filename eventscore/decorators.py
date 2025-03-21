from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Type, TypeVar

from eventscore.core.abstract import IECore
from eventscore.core.events import Event

TEvent = TypeVar("TEvent", bound=Event)
TFunc = TypeVar("TFunc", bound=Callable)
TConsumerGroup = TypeVar("TConsumerGroup", bound=str)


def event(cls: Type[TEvent] | None = None) -> Type[TEvent]:
    def wrap(cls: Type[TEvent]) -> Type[TEvent]:
        return dataclass(frozen=True)(cls)

    if cls is None:
        return wrap  # type:ignore[return-value]

    return wrap(cls)


def consumer(
    func: TFunc | None = None,
    *,
    ecore: IECore,
    event: TEvent,
    consumer_group: TConsumerGroup,
    clones: int = 1,
) -> TFunc:
    def decorator(func: TFunc) -> TFunc:
        ecore.register_consumer(func, event, consumer_group, clones)

    if func is None:
        return decorator

    return decorator(func)
