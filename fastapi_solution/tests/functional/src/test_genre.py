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
async def test_get_genre(es_write_data, make_get_request, es_delete_data, get_redis_data, clear_redis_cash):
    await es_write_data(data, index)
    response = await make_get_request(method=index, params=data[0])
    assert response.body['id'] == data[0]['id']
    assert response.body['name'] == data[0]['name']
    await es_delete_data(method=index, params=data[0])
    redis_data = await get_redis_data(index, data[0]['id'])
    assert redis_data['id'] == data[0]['id']
    assert redis_data['name'] == data[0]['name']
    await clear_redis_cash(index, data[0]['id'])
