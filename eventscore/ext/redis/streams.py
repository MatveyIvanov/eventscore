from collections import defaultdict
from typing import Any, Dict, Mapping

import redis
from redis.typing import EncodableT, FieldT

from eventscore.core.abstract import EventType, IEventSerializer, IStream
from eventscore.core.exceptions import EmptyStreamError
from eventscore.core.types import Event


class RedisStream(IStream):
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        serializer: IEventSerializer[bytes, Dict[FieldT, EncodableT]],
        redis_init_kwargs: Mapping[str, Any] | None = None,
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

    def put(
        self,
        event: Event,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> None:
        self.__redis.xadd(
            name=event.type,
            fields=self.__serializer.encode(event),
            id=str(event.uid),
        )

    def pop(
        self,
        event: EventType,
        *,
        block: bool = True,
        timeout: int = 5,
    ) -> Event:
        xresult = self.__redis.xread(
            streams={event: self.__event_to_latest_id[event]},
            block=timeout * 1000 if block else None,
        )
        print(xresult, type(xresult))
        if not xresult:
            raise EmptyStreamError

        id_, bevent = xresult[0]
        self.__event_to_latest_id[event] = id_
        return self.__serializer.decode(bevent)
