from fastapi import APIRouter
from models.base import AbstractModel
from pydantic.schema import Optional
from pydantic import Field

router = APIRouter()


class FilmShort(AbstractModel):
    title: str
    imdb_rating: Optional[float] = Field(alias='rating')
