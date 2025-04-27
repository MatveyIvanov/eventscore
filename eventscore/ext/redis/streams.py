import logging
import multiprocessing as mp
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from multiprocessing.synchronize import (
        _LockLike,  # pyright:ignore[reportPrivateUsage]
    )

from redis import Redis

from eventscore.core.abstract import ConsumerGroup, EventType, IEventSerializer, IStream
from eventscore.core.exceptions import EmptyStreamError, TooManyDataError
from eventscore.core.logging import logger as _logger
from eventscore.core.types import Event

XReadT: TypeAlias = list[tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]]]]


class RedisStream(IStream):
    def __init__(
        self,
        *,
        serializer: IEventSerializer[bytes, str],
        redis: Redis | None = None,
        host: str | None = None,
        port: int | None = None,
        db: int | None = None,
        redis_init_kwargs: dict[str, Any] | None = None,
        logger: logging.Logger = _logger,
    ) -> None:
        """
        Construct Redis stream instance

        :param host: Redis host
        :type host: str
        :param port: Redis port
        :type port: int
        :param db: Redis database
        :type db: int
        :param serializer: Event serializer
        :type serializer: IEventSerializer[bytes, str]
        :param redis_init_kwargs: Redis initialization kwargs
        :type redis_init_kwargs: dict[str, Any] | None
        """
        assert redis is not None or (
            host is not None and port is not None and db is not None
        ), "Redis instance or required params for its constructing are required."

        redis_init_kwargs = redis_init_kwargs or {}
        redis_init_kwargs.update(
            dict(
                host=host,
                port=port,
                db=db,
            )
        )
        self.__redis = redis or Redis(**redis_init_kwargs)
        self.__serializer = serializer
        self.__event_n_group_to_latest_id: dict[
            tuple[EventType, ConsumerGroup], str
        ] = defaultdict(lambda: "0")
        self.__event_n_group_to_lock: dict[
            tuple[EventType, ConsumerGroup], _LockLike
        ] = defaultdict(lambda: mp.Lock())
        self.__logger = logger

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        _ = self.__redis.xadd(
            name=str(event.type),
            fields={"value": self.__serializer.encode(event)},
        )
        self.__logger.debug(f"XADDed event {event}.")

    def pop(
        self,
        event: EventType,
        group: ConsumerGroup,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        self.__logger.debug(
            f"About to xread an event. Stream {id(self)}, "
            + f"latest ID {self.__event_n_group_to_latest_id[(event, group)]}."
        )
        with self.__lock(event, group):
            xresult: XReadT = self.__redis.xread(
                streams={
                    str(event): self.__event_n_group_to_latest_id[
                        (event, group)
                    ]  # type:ignore # noqa:E501
                },
                count=1,
                block=timeout * 1000 if block else None,
            )
            self.__logger.debug(f"XREADed {xresult}.")
            if not xresult:
                raise EmptyStreamError

            item = xresult[0]
            if not item:
                raise EmptyStreamError

            name, data = item
            if not data:
                raise EmptyStreamError
            if len(data) > 1:
                raise TooManyDataError

            uid, payload = data[0]
            self.__event_n_group_to_latest_id[(event, group)] = uid.decode()

        bevent = payload[b"value"]
        self.__logger.debug(f"Got valid event {name.decode()} with id {uid.decode()}.")
        return self.__serializer.decode(bevent)

    @contextmanager
    def __lock(self, event: EventType, group: ConsumerGroup) -> Iterator[None]:
        _ = self.__event_n_group_to_lock[(event, group)].acquire()
        try:
            yield
        finally:
            self.__event_n_group_to_lock[(event, group)].release()
