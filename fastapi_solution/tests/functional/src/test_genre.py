import pytest


index = 'genre'
data = [{'id': 'b58ay2b8-d644-7581-cmy9-2astry34343', 'name': 'Test genre'}]


@pytest.mark.asyncio
async def test_get_all_genres(make_get_request):
    response = await make_get_request(method=index)
    assert response.status == 200
    assert len(response.body) > 1


@pytest.mark.asyncio
async def test_get_genre(es_write_data, make_get_request):
    await es_write_data(data, index)
    await make_get_request(method=index, params=data[0])

