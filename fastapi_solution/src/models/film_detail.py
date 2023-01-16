from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from models.base import AbstractModel
from models.person import PersonShort
from services.film import FilmService, get_film_service
from pydantic.schema import Optional, List

router = APIRouter()


class FilmShort(AbstractModel):
    title: str
    imdb_rating: Optional[float]


class FilmDetail(AbstractModel):
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float]
    actors: Optional[List[PersonShort]] = None
    writers: Optional[List[PersonShort]] = None
    director: Optional[List] = None
    genre: Optional[List] = None
    actors_names: Optional[List] = None
    writers_names: Optional[List] = None


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=FilmDetail)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
        # Которое отсутствует в модели ответа API.
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны
        # и, возможно, данные, которые опасно возвращать
    return FilmDetail(id=film.id, title=film.title)
