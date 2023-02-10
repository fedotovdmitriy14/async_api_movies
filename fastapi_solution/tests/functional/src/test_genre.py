from http import HTTPStatus

import pytest

index = 'genres'
data = [{'id': '0031feab-8f53-412a-8f53-47098a60ac73', 'name': 'Test genre'},]


@pytest.mark.asyncio
async def test_get_all_genres(make_get_request):
    response = await make_get_request(method=index)
    assert response.get('status') == 200
    assert len(response.get('body')) > 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '00af52ec-9345-4d66-adbe-50eb917f463a', 'not_valid_uuid'
))
async def test_get_genre_not_valid(make_get_request, uuid):
    response = await make_get_request(f'{index}/{uuid}')
    assert response.get('status') == 404


@pytest.mark.asyncio
async def test_get_genre(make_get_request, es_write_data, redis_client):
    await es_write_data(data, index)
    genre_id = data[0].get('id')
    response = await make_get_request(method=f'{index}/{genre_id}')
    assert response.get('status') == 200
    assert response.get('body')['id'] == genre_id
    assert response.get('body')['name'] == data[0].get('name')
    await es_write_data(data, index, delete=True)
    response = await make_get_request(method=f'{index}/{genre_id}')
    assert response.get('status') == 200
    assert response.get('body')['id'] == genre_id
    assert response.get('body')['name'] == data[0].get('name')


@pytest.mark.asyncio
async def test_get_cache_genre(make_get_request, es_write_data, es_client, redis_cache_clear):
    await es_write_data(data, index)
    genre_id = data[0].get('id')
    response_1 = await make_get_request(method=f'{index}/{genre_id}')
    assert response_1.get('status') == HTTPStatus.OK
    await es_client.delete('genres', genre_id)
    response_2 = await make_get_request(method=f'{index}/{genre_id}')
    assert response_2['status'] == HTTPStatus.OK
    assert response_1['body'] == response_2['body']
