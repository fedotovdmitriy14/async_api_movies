from http import HTTPStatus

import pytest

from tests.functional.utils.helpers import make_get_request, es_write_data

index = 'genres'
data = [{'id': '0031feab-8f53-412a-8f53-47098a60ac73', 'name': 'Test genre'},]


@pytest.mark.asyncio
async def test_get_all_genres(client_session):
    response = await make_get_request(client_session, method=index)
    assert response.get('status') == 200
    assert len(response.get('body')) > 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '00af52ec-9345-4d66-adbe-50eb917f463a', 'not_valid_uuid'
))
async def test_get_genre_not_valid(client_session, uuid):
    response = await make_get_request(client_session, f'{index}/{uuid}')
    assert response.get('status') == 404


@pytest.mark.asyncio
async def test_get_genre(es_client, client_session):
    await es_write_data(es_client, data, index)
    genre_id = data[0].get('id')
    response = await make_get_request(client_session, method=f'{index}/{genre_id}')
    assert response.get('status') == 200
    assert response.get('body')['id'] == genre_id
    assert response.get('body')['name'] == data[0].get('name')


@pytest.mark.asyncio
async def test_get_cache_genre(client_session, es_client):
    await es_write_data(es_client, data, index)
    genre_id = data[0].get('id')
    response_1 = await make_get_request(client_session, method=f'{index}/{genre_id}')
    assert response_1.get('status') == HTTPStatus.OK
    await es_client.delete('genres', genre_id)
    response_2 = await make_get_request(client_session, method=f'{index}/{genre_id}')
    assert response_2['status'] == HTTPStatus.OK
    assert response_1['body'] == response_2['body']
