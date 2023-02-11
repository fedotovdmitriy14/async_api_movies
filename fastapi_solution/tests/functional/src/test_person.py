from http import HTTPStatus

import pytest


index = 'persons'
data = [{'id': '54028227-35e9-4d5e-9184-e342f2861a73', 'name': 'Test Person'}]
search_film_url_path = 'persons/search/'

film_data = [
    {
        "id": "086b41fc-9fed-4dd8-9dfd-24730dc3b7e8",
        "title": "Test Person Film",
        "imdb_rating": 6.8,
        "description": "Test Description",
        "actors": [
            {
                "id": "54028227-35e9-4d5e-9184-e342f2861a73",
                "name": "Test Person"
            },
        ],
        "writers": [
            {
                "id": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a",
                "name": "George Lucas"
            }
        ],
        "director": [
            "George Lucas"
        ],
        "genre": [
            {
                "id": "120a21cf-9097-479e-904a-13dd7198c1dd",
                "name": "Adventure"
            },
        ],
        "actors_names": [
            "Carrie Fisher",
            "Harrison Ford"
        ],
        "writers_names": [
            "George Lucas"
        ]
    }
]


@pytest.mark.asyncio
async def test_get_all_persons(es_write_data, make_get_request):
    await es_write_data(data, index)
    response = await make_get_request(method=index)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '0d40fb5d-d456-47c0-84c5-5929e74189ff', 'not_valid_uuid'
))
async def test_get_persons_not_valid(es_write_data, make_get_request, uuid):
    await es_write_data(data, index)
    response = await make_get_request(method=f'{index}/{uuid}')
    assert response.get('status') == 404


@pytest.mark.asyncio
async def test_get_person(es_write_data, make_get_request):
    await es_write_data(data, index)
    person_id = data[0].get('id')
    response = await make_get_request(method=f'{index}/{person_id}')
    assert response.get('status') == 200
    assert response.get('body')['id'] == person_id
    assert response.get('body')['name'] == data[0].get('name')


@pytest.mark.asyncio
async def test_get_cache_person(es_write_data, es_client, make_get_request):
    await es_write_data(data, index)
    person_id = data[0].get('id')
    response_1 = await make_get_request(method=f'{index}/{person_id}')
    assert response_1.get('status') == HTTPStatus.OK
    await es_client.delete('persons', person_id)
    response_2 = await make_get_request(method=f'{index}/{person_id}')
    assert response_2['status'] == HTTPStatus.OK
    assert response_1['body'] == response_2['body']


# @pytest.mark.asyncio
# async def test_get_persons_film(es_write_data, make_get_request):
#     film_id = film_data[0]['id']
#     data[0]["film_ids"] = [film_id, ]
#     await es_write_data(film_data, 'movies')
#     await es_write_data(data, index)
#     person_id = data[0].get('id')
#     response = await make_get_request(method=f'{index}/{person_id}/film')
#     assert response.get('status') == 200
#     assert response.get('body')[0]['id'] == film_id
#     assert response.get('body')[0]['title'] == film_data[0].get('title')


@pytest.mark.asyncio
async def test_get_all_persons_search_with_pagination(es_write_data, make_get_request):
    await es_write_data(data, index)
    params = {'page[size]': 1, 'page[number]': 1}
    response = await make_get_request(method=search_film_url_path, params=params)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page_number,page_size",
    (
        (-1, 1),
        (1, -1),
        (0, 0),
        (-1, -1),
    ),
)
async def test_persons_invalid_pagination(es_write_data, make_get_request, page_number, page_size):
    await es_write_data(data, index)
    params = {'page[size]': page_size, 'page[number]': page_number}
    response = await make_get_request(method=search_film_url_path, params=params)
    assert response.get('status') == 422


@pytest.mark.asyncio
async def test_search_persons_by_title(es_write_data, make_get_request):
    params = {'query': 'Test Person'}
    await es_write_data(data, index)
    person_id = data[0].get('id')
    response = await make_get_request(method=search_film_url_path, params=params)
    assert response.get('status') == 200
    assert response.get('body')[0]['id'] == person_id
