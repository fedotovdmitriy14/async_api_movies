import asyncio
from typing import List

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch, helpers

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import get_es_bulk_query
from tests.functional.utils.wait_for_es import wait_for_es
from tests.functional.utils.wait_for_redis import wait_for_redis


@pytest.fixture(scope='session')
async def es_client():
    await wait_for_es()
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic_host}:{test_settings.elastic_port}'])
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def redis_client():
    await wait_for_redis()
    client = await aioredis.create_redis_pool((test_settings.redis_host, test_settings.redis_port),
                                              minsize=10, maxsize=20)
    yield client
    client.flushdb()
    client.close()


@pytest.fixture
def get_redis_data(redis_client):
    async def inner(index_name: str, item_id: str):
        client = await redis_client
        return client.get(f'{index_name}::{item_id}')
    return inner


@pytest.fixture
def clear_redis_cash(redis_client):
    async def inner(index_name: str, item_id: str):
        client = await redis_client
        client.delete(f'{index_name}::{item_id}')
    return inner


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: List[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index)
        client = await es_client()
        response = await client.bulk(bulk_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
        await asyncio.sleep(1)
    return inner


@pytest.fixture
def es_delete_data(es_client):
    async def inner(data: List[dict], es_index: str):
        await helpers.async_bulk(es_client,
                                 [{'_op_type': 'delete', '_index': es_index, '_id': item['id']} for item in data])

    return inner


@pytest.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(client_session):
    async def inner(method: str, params: dict):
        url = f'http://{test_settings.elastic_host}:{test_settings.elastic_port}/api/v1/{method}'
        session = await client_session()
        async with session.get(url, params=params) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
        return dict(body=body, headers=headers, status=status)
    return inner

