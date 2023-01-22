from typing import Optional
from fastapi import APIRouter, Depends, Query

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
