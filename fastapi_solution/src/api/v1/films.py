from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import FilmShort, FilmDetail
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=FilmDetail,
    description='Film detailed info',
    summary='Get detailed film by id',
)
async def get_one_film(
        film_id: str,
        film_service: FilmService = Depends(get_film_service),
) -> FilmDetail:
    response = await film_service.get_by_id(film_id=film_id)
    return FilmDetail(**response)


@router.get(
    '/',
    response_model=list[FilmShort],
    description='All films info',
    summary='Get all films',
)
async def get_all_films(
        sort: Optional[str] = Query(default=None),
        filter_genre: Optional[str] = Query(None, alias='filter[genre]'),
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    response = await film_service.get_all_films(
        sort=sort,
        filter_genre=filter_genre
    )
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return response


@router.get(
    '/search/',
    response_model=list[FilmShort],
    description='Search films',
    summary='Search films with pagination and query for title',
)
async def search_films(
        query: Optional[str] = Query(default=None),
        page_number: Optional[int] = Query(None, alias='page[number]'),
        page_size: Optional[int] = Query(None, alias='page[size]'),
        film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    response = await film_service.get_sorted_films(
        page_size=page_size,
        page_number=page_number,
        query=query,
    )
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return response
