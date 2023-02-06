import json
from typing import List

from elasticsearch.helpers import async_bulk, BulkIndexError
from elasticsearch.helpers import bulk

from tests.functional.settings import test_settings


def get_es_bulk_query(es_data, es_index):
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row['id']}}),
            json.dumps(row)
        ])
    return '\n'.join(bulk_query) + '\n'


async def make_get_request(client_session, method: str, params: dict = None):
    if not params:
        params = {}
    url = f'http://{test_settings.elastic_host}:{test_settings.fastapi_port}/api/v1/{method}'
    async with client_session.get(url, params=params) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    return dict(body=body, headers=headers, status=status)


async def es_write_data(es_client, data: List[dict], es_index: str):
    try:
        await async_bulk(es_client, data, index=es_index)
    except BulkIndexError:
        raise Exception('Ошибка записи данных в Elasticsearch')
