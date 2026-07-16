import redis

from config import (
    REDIS_CRAWLED_URLS_KEY,
    REDIS_DB,
    REDIS_DETAIL_URLS_KEY,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)


class RedisDeduper:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )

    def is_new_detail_url(self, url):
        return self.client.sadd(REDIS_DETAIL_URLS_KEY, url) == 1

    def is_crawled(self, url):
        return self.client.sismember(REDIS_CRAWLED_URLS_KEY, url)

    def mark_crawled(self, url):
        return self.client.sadd(REDIS_CRAWLED_URLS_KEY, url)