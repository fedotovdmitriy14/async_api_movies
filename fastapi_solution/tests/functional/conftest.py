import asyncio
from typing import List, Optional

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import get_es_bulk_query
from tests.functional.utils.wait_for_es import wait_for_es
import pytest_asyncio


@pytest_asyncio.fixture(scope='session')
async def es_client():
    wait_for_es()
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic_host}:{test_settings.elastic_port}'])
    yield client
    await client.close()


@pytest_asyncio.fixture
def es_write_data(es_client):
    async def inner(data: List[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index)
        client = await es_client()
        response = await client.bulk(bulk_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
        await asyncio.sleep(1)
        yield
    return inner


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


@pytest_asyncio.fixture
def make_get_request(client_session):
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
