import time

import aioredis

from tests.functional.settings import test_settings


async def wait_for_redis():
    redis_client = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port),
                                                    minsize=10, maxsize=20)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
