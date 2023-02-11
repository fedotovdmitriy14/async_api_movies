from http import HTTPStatus

import pytest

from tests.functional.utils.helpers import make_get_request, es_write_data

search_film_url_path = 'films/search/'
film_url_path = 'films'
index_name = 'movies'
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
async def test_get_all_films(es_client, client_session):
    await es_write_data(es_client, data, es_index=index_name)
    response = await make_get_request(client_session, method=film_url_path)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('uuid', (
    '00af52ec-9345-4d66-adbe-50eb917f463a6', 'not_valid_uuid'
))
async def test_get_film_not_valid(client_session, uuid):
    response = await make_get_request(client_session, f'{film_url_path}/{uuid}')
    assert response.get('status') == 404


@pytest.mark.asyncio
async def test_get_film(es_client, client_session):
    await es_write_data(es_client, data, es_index='movies')
    film_id = data[0].get('id')
    response = await make_get_request(client_session, method=f'{film_url_path}/{film_id}')
    assert response.get('status') == 200
    assert response.get('body')['id'] == film_id


@pytest.mark.asyncio
async def test_get_cache_film(client_session, es_client):
    await es_write_data(es_client, data, film_url_path)
    film_id = data[0].get('id')
    response_1 = await make_get_request(client_session, method=f'{film_url_path}/{film_id}')
    assert response_1.get('status') == HTTPStatus.OK
    await es_client.delete('movies', film_id)
    response_2 = await make_get_request(client_session, method=f'{film_url_path}/{film_id}')
    assert response_2['status'] == HTTPStatus.OK
    assert response_1['body'] == response_2['body']


@pytest.mark.asyncio
async def test_get_all_films_search(es_client, client_session):
    await es_write_data(es_client, data, es_index=index_name)
    response = await make_get_request(client_session, method=search_film_url_path)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
async def test_get_all_films_search_with_pagination(es_client, client_session):
    params = {'page[size]': 1, 'page[number]': 1}
    await es_write_data(es_client, data, es_index=index_name)
    response = await make_get_request(client_session, method=search_film_url_path, params=params)
    assert response.get('status') == 200
    assert len(response.get('body')) == 1


@pytest.mark.asyncio
async def test_search_film_by_title(es_client, client_session):
    params = {'query': 'test title'}
    await es_write_data(es_client, data, es_index=index_name)
    film_id = data[0].get('id')
    response = await make_get_request(client_session, method=f'{search_film_url_path}', params=params)
    assert response.get('status') == 200
    assert response.get('body')[0]['id'] == film_id


@pytest.mark.asyncio
async def test_get_all_films_search_with_invalid_page_size(client_session):
    params = {'page[size]': -1, 'page[number]': 1}
    response = await make_get_request(client_session, method=search_film_url_path, params=params)
    assert response.get('status') == 422


@pytest.mark.asyncio
async def test_get_all_films_search_with_invalid_page_number(client_session):
    params = {'page[size]': 1, 'page[number]': -1}
    response = await make_get_request(client_session, method=search_film_url_path, params=params)
    assert response.get('status') == 422
