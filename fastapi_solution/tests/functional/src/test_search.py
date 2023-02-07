import pytest

from tests.functional.utils.helpers import make_get_request, es_write_data

index = 'films/search/'
data = [
    {
        "id": "65f01393-dd19-4b83-9703-d7764d33e489",
        "title": "Test Title",
        "imdb_rating": 8.6,
        "description": "Test Description",
        "actors": [
            {
                "id": "26e83050-29ef-4163-a99d-b546cac208f8",
                "name": "Mark Hamill"
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
async def test_get_all_films_search(client_session):
    response = await make_get_request(client_session, method=index)
    assert response.get('status') == 200
    assert len(response.get('body')) > 1


@pytest.mark.asyncio
async def test_get_all_films_search_with_pagination(client_session):
    params = {'page[size]': 1, 'page[number]': 1}
    response = await make_get_request(client_session, method=index, params=params)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
async def test_get_film_by_name(es_client, client_session):
    params = {'query': 'test title'}
    await es_write_data(es_client, data, es_index='movies')
    film_id = data[0].get('id')
    response = await make_get_request(client_session, method=f'{index}', params=params)
    assert response.get('status') == 200
    assert response.get('body')[0]['id'] == film_id
