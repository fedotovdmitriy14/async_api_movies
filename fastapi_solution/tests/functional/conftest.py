from typing import List

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.utils.helpers import get_es_bulk_query


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'http://{test_settings.elastic_host}:{test_settings.elastic_port}'])
    yield client
    await client.close()


@pytest.fixture
def es_write_data(es_client):

    async def inner(data: List[dict]):
        bulk_query = get_es_bulk_query(data, test_settings.es_index, test_settings.es_id_field)
        client = await es_client()
        response = await client.bulk(bulk_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture(scope='session')
async def client_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(client_session):
    url = f'{test_settings.elastic_host}:{test_settings.elastic_port}/api/v1/search'
    query_data = {'search': 'The Star'}
    session = await client_session()
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    return dict(body=body, headers=headers, status=status)
