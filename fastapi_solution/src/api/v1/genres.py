from fastapi import APIRouter, Depends

from src.models.genre import Genre
from src.services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get(
    path="/",
    response_model=list[Genre],
    summary="Get all genres",
    description="All genres",
)
async def get_genres(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    return await genre_service.get_all(
        model=Genre,
        index_name='genres',
    )


@router.get(
    '/{genre_id}',
    response_model=Genre,
    description='Genre detailed info',
    summary='Get genre by id',
)
async def get_one_genre(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service),
) -> Genre:
    return await genre_service.get_by_id(
        id_=genre_id,
        model=Genre,
        index_name='genres',
    )
