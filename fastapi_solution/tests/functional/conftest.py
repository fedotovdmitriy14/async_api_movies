import asyncio

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from typing import List

from elasticsearch.helpers import async_bulk, BulkIndexError
from tests.functional.settings import test_settings
import pytest_asyncio


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic_host}:{test_settings.elastic_port}'])
    yield client
    await client.close()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    redis_client = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port),
                                                    minsize=10, maxsize=20)
    yield redis_client
    await redis_client.close()


@pytest_asyncio.fixture
async def es_write_data(es_client):
    async def inner(data: List[dict], es_index: str, delete=False):
        await es_client.delete_by_query(index=es_index, body={"query": {"match_all": {}}})
        if not delete:
            documents = [{"_index": es_index, "_id": row['id'], "_source": row} for row in data]
        else:
            documents = [{'_op_type': 'delete', '_index': es_index, '_id': row['id']} for row in data]
        try:
            await async_bulk(es_client, documents, refresh=True)
        except BulkIndexError:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture
async def make_get_request(client_session):
    async def inner(method: str, params: dict = None):
        if not params:
            params = {}
        url = f'http://{test_settings.elastic_host}:{test_settings.fastapi_port}/api/v1/{method}'
        async with client_session.get(url, params=params) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return dict(body=body, headers=headers, status=status)
    return inner
