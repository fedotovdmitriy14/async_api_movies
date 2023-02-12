from typing import List

import pytest_asyncio
from elasticsearch._async.helpers import async_bulk
from elasticsearch.helpers import BulkIndexError

from tests.functional.settings import test_settings


@pytest_asyncio.fixture
async def es_write_data(es_client):
    async def inner(data: List[dict], es_index: str, delete=False):
        await es_client.delete_by_query(index=es_index, conflicts='proceed', body={"query": {"match_all": {}}})
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
