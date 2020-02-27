import os
from shared.settings.databasesconf import DATABASES

CACHE_REDIS_CONFIGURATION = {
    "HOST": os.environ.get('CACHEREDIS_DEFAULT_HOSTNAME', 'localhost'),
    "PORT": os.environ.get('CACHEREDIS_DEFAULT_PORT', 6379),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            "SOCKET_TIMEOUT": 5,  # in seconds
        }
    }
}

ALLOWED_HOSTS = ['localhost', '40.115.100.253', '130.192.85.198', '127.0.0.1']
INTERNAL_IPS = ('0.0.0.0')
