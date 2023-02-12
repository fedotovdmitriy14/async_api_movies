from http import HTTPStatus

import pytest

index = 'genres'
data = [{'id': '0031feab-8f53-412a-8f53-47098a60ac73', 'name': 'Test genre'}]


@pytest.mark.asyncio
async def test_get_all_genres(es_write_data, make_get_request):
    await es_write_data(data, index)
    response = await make_get_request(method=index)
    assert response.get('status') == HTTPStatus.OK
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '00af52ec-9345-4d66-adbe-50eb917f463a', 'not_valid_uuid'
))
async def test_get_genre_not_valid(es_write_data, make_get_request, uuid):
    await es_write_data(data, index)
    response = await make_get_request(f'{index}/{uuid}')
    assert response.get('status') == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_genre(es_client, make_get_request, es_write_data):
    await es_write_data(data, index)
    genre_id = data[0].get('id')
    response = await make_get_request(method=f'{index}/{genre_id}')
    assert response.get('status') == HTTPStatus.OK
    assert response.get('body')['id'] == genre_id
    assert response.get('body')['name'] == data[0].get('name')
    await es_client.delete(index, genre_id)
    response = await make_get_request(method=f'{index}/{genre_id}')
    assert response.get('status') == HTTPStatus.OK
    assert response.get('body')['id'] == genre_id
    assert response.get('body')['name'] == data[0].get('name')
