from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.models.film import FilmShort, FilmDetail
# from src.services.film import FilmService, get_film_service
from src.services.base_service import BaseService, get_service

router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=FilmDetail,
    description='Film detailed info',
    summary='Get detailed film by id',
)
async def get_one_film(
        film_id: str,
        film_service: BaseService = Depends(get_service),
) -> FilmDetail:
    return await film_service.get_by_id(
        id_=film_id,
        model=FilmDetail,
        index_name='movies',
    )


@router.get(
    '/',
    response_model=list[FilmShort],
    description='All films info',
    summary='Get all films',
)
async def get_all_films(
        sort: Optional[str] = Query(default=None),
        filter_genre: Optional[str] = Query(None, alias='filter[genre]'),
        film_service: BaseService = Depends(get_service),
) -> list[FilmShort]:
    return await film_service.get_all(
        sort=sort,
        filter_genre=filter_genre,
        model=FilmShort,
        index_name='movies',
    )


@router.get(
    '/search/',
    response_model=list[FilmShort],
    description='Search films',
    summary='Search films with pagination and query for title',
)
async def search_films(
        query: Optional[str] = Query(default=None),
        page_number: Optional[int] = Query(alias='page[number]', default=1, gt=0),
        page_size: Optional[int] = Query(alias='page[size]', default=10, gt=0, lt=10000),
        film_service: BaseService = Depends(get_service),
) -> list[FilmShort]:
    return await film_service.get_sorted_films(
        page_size=page_size,
        page_number=page_number,
        query=query,
    )
