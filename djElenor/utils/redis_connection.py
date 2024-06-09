import json

import redis
from django.conf import settings

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def redis_set(key: str, data: str, ex: int = 120) -> str:
    items = redis_instance.set(key, data, ex)
    return items


def redis_get(key: str) -> str:
    item = redis_instance.get(key)
    if item:
        item = json.loads(item)
    return item


def redis_delete(key):
    _ = redis_instance.delete(key)
    return True
