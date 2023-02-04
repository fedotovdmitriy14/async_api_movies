from http import HTTPStatus

import pytest


index = 'genre'
data = [{'id': 'b58ay2b8-d644-7581-cmy9-2astry34343', 'name': 'Test genre'}]


@pytest.mark.asyncio
async def test_get_all_genres(make_get_request):
    response = await make_get_request(method=index)
    assert response.status == 200
    assert len(response.body) > 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '00af52ec-9345-4d66-adbe-50eb917f463a', 'not_valid_uuid'
))
async def test_get_genre_not_valid(make_get_request, uuid):
    response = await make_get_request(f'{index}/{uuid}')
    assert response.status != 200


@pytest.mark.asyncio
async def test_get_genre(es_write_data, make_get_request):
    await es_write_data(data, index)
    genre_id = data[0].get('id')
    response = await make_get_request(method=index, params=data[0])
    assert response.status == HTTPStatus.OK
    assert response.body['uuid'] == genre_id
    assert response.body['name'] == data[0].get('name')


@pytest.mark.asyncio
async def test_get_cache_genre(es_write_data, es_client, make_get_request, redis_client):
    await es_write_data(data, index)
    genre_id = data[0].get('id')
    response_1 = await make_get_request(f'/genres/{genre_id}/')
    assert response_1.status == HTTPStatus.OK
    await es_client.delete('genres', genre_id)
    response_2 = await make_get_request(f'/genres/{genre_id}/')
    assert response_2.status == HTTPStatus.OK
    assert response_1.body == response_2.body
