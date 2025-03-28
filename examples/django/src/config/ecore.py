from eventscore.core.ecore import ECore
from eventscore.ext.redis.serializers import RedisEventSerializer
from eventscore.ext.redis.streams import RedisStream

serializer = RedisEventSerializer()
stream = RedisStream(host="redis", port=6379, db=0, serializer=serializer)

ecore = ECore(stream=stream)
