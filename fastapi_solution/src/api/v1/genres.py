from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

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
    sort: Optional[str] = Query("name", alias="sort"),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[Genre]:
    es_genres = await genre_service.get_genres(sort)
    if not es_genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    genres = [Genre(uuid=genre.uuid, name=genre.name) for genre in es_genres]
    return genres
