import os

from eventscore.core.ecore import ECore
from eventscore.ext.redis.serializers import RedisEventSerializer
from eventscore.ext.redis.streams import RedisStream

serializer = RedisEventSerializer()
stream = RedisStream(
    host="redis",
    port=6379,
    db=0,
    serializer=serializer,
    redis_init_kwargs={"password": os.environ["REDIS_PASSWORD"]},
)

ecore = ECore(stream=stream)
ecore.discover_consumers()
ecore.spawn_workers()

