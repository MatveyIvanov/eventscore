from collections import defaultdict
from typing import Any, Dict

import redis

from eventscore.core.abstract import EventType, IEventSerializer, IStream
from eventscore.core.exceptions import EmptyStreamError, TooManyDataError
from eventscore.core.types import Event
from eventscore.core.logging import logger


class RedisStream(IStream):
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        serializer: IEventSerializer[bytes, str],
        redis_init_kwargs: Dict[str, Any] | None = None,
    ) -> None:
        redis_init_kwargs = redis_init_kwargs or {}
        redis_init_kwargs.update(
            dict(
                host=host,
                port=port,
                db=db,
            )
        )
        self.__redis = redis.Redis(**redis_init_kwargs)
        self.__serializer = serializer
        self.__event_to_latest_id = defaultdict(lambda: 0)
        self.__logger = logger

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        self.__redis.xadd(
            name=str(event.type),
            fields={"value": self.__serializer.encode(event)},
            # id=str(event.uid),
        )
        self.__logger.debug(f"XADDed event {event}.")

    def pop(
        self,
        event: EventType,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        xresult = self.__redis.xread(
            streams={event: self.__event_to_latest_id[event]},
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
        bevent = payload[b"value"]

        self.__logger.debug(f"Got valid event {name} with id {uid}.")
        self.__event_to_latest_id[event] = uid
        return self.__serializer.decode(bevent)
