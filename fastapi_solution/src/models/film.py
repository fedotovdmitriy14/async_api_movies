from fastapi import APIRouter
from pydantic.schema import Optional, List

from src.models.base import AbstractModel
from src.models.genre import Genre
from src.models.person import PersonShort

router = APIRouter()


class FilmShort(AbstractModel):
    title: str
    imdb_rating: Optional[float]


class FilmDetail(FilmShort):
    description: Optional[str] = None
    actors: Optional[List[PersonShort]] = None
    writers: Optional[List[PersonShort]] = None
    director: Optional[List] = None
    genre: Optional[List[Genre]] = None
    actors_names: Optional[List] = None
    writers_names: Optional[List] = None
