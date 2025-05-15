import logging
import os

from eventscore.core.ecore import ECore
from eventscore.core.logging import logger
from eventscore.core.streams import StreamFactory
from eventscore.ext.redis.serializers import RedisEventSerializer
from eventscore.ext.redis.streams import RedisStream

serializer = RedisEventSerializer()
stream_factory = StreamFactory(
    stream_class=RedisStream,
    kwargs=dict(
        host="redis",
        port=6379,
        db=0,
        serializer=serializer,
        redis_init_kwargs={"password": os.environ["REDIS_PASSWORD"]},
    ),
)
logger.setLevel(logging.INFO)
ecore = ECore(stream_factory=stream_factory, logger=logger)
# One way of registering consumers,
# no explicit registering required
ecore.discover_consumers()
ecore.spawn_workers()
