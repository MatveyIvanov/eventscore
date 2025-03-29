import functools
from typing import Any

from eventscore.core.abstract import ConsumerFunc, ConsumerGroup, EventType, IECore


def consumer(
    func: ConsumerFunc | None = None,
    *,
    ecore: IECore,
    event: EventType,
    group: ConsumerGroup,
    clones: int = 1,
) -> ConsumerFunc:
    def decorator(func: ConsumerFunc) -> ConsumerFunc:
        ecore.register_consumer(func, event, group, clones)

        setattr(func, "__is_consumer__", True)
        setattr(func, "__consumer_event__", event)
        setattr(func, "__consumer_group__", group)
        setattr(func, "__consumer_clones__", clones)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator  # type:ignore[return-value]

    return decorator(func)
