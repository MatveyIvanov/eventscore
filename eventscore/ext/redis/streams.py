import logging
import os
from collections import defaultdict
from typing import TYPE_CHECKING, Any, TypeAlias

import redis

if TYPE_CHECKING:
    pass

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
        self.__event_n_group_to_xgroup: dict[tuple[EventType, ConsumerGroup], bool] = (
            defaultdict(bool)
        )
        self.__logger = logger
        self.__name = str(os.getpid())

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
        self.__logger.debug(f"About to xread an event. Stream {id(self)}")
        self.__ensure_xgroup(event, group)
        xresult: XReadT = self.__redis.xreadgroup(  # type:ignore[assignment]
            groupname=str(group),
            consumername=self.__name,
            streams={str(event): ">"},
            count=1,
            block=timeout * 1000 if block else None,
        )
        self.__logger.debug(f"XREADedGROUP {xresult}.")
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
        _ = self.__redis.xack(str(event), str(group), uid)
        bevent = payload[b"value"]
        self.__logger.debug(
            f"Received valid event {name.decode()} with id {uid.decode()}."
        )
        return self.__serializer.decode(bevent)

    def __ensure_xgroup(self, event: EventType, group: ConsumerGroup) -> None:
        if self.__event_n_group_to_xgroup[(event, group)]:
            return
        try:
            _ = self.__redis.xgroup_create(
                name=str(event),
                groupname=str(group),
                # TODO: make this configurable,
                #  otherwise restart will cause duplicate reads
                id="0",
                mkstream=True,
            )
        except redis.ResponseError:
            self.__event_n_group_to_xgroup[(event, group)] = True
            self.__logger.debug(f"XGROUP already created for {(event, group)}.")
        else:
            self.__event_n_group_to_xgroup[(event, group)] = True
            self.__logger.debug(f"XGROUP created for {(event, group)}.")
