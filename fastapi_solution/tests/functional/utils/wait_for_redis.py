from redis import asyncio as aioredis

from tests.functional.settings import test_settings
from tests.functional.utils.backoff import backoff


@backoff()
async def wait_for_redis():
    redis_client = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port),
                                                    minsize=10, maxsize=20)
    try:
        return redis_client.ping()
    except Exception as e:
        raise e


if __name__ == '__main__':
    wait_for_redis()
