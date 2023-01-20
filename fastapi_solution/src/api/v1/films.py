from http import HTTPStatus
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

# Объект router, в котором регистрируем обработчики
from src.db.elastic import get_elastic
from src.models.film import FilmShort
from src.services.film import FilmService

router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах


# Модель ответа API
class Film(BaseModel):
    id: str
    title: str


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/film/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса (film_id: str)
# И указываем тип возвращаемого объекта — Film
@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str) -> Film:
    return Film(id='some_id', title='some_title')


@router.get('/', response_model=list[FilmShort])
async def get_all_films(
        sort: Optional[str] = Query(default=None),
        page_number: Optional[int] = Query(None, alias='page[number]'),
        page_size: Optional[int] = Query(None, alias='page[size]'),
        filter_genre: Optional[str] = Query(None, alias='filter[genre]'),
        db: AsyncElasticsearch = Depends(get_elastic),
):
    films = FilmService(redis=None, elastic=db)
    response = await films.get_all_films(
        sort=sort,
        page_size=page_size,
        page_number=page_number,
        filter_genre=filter_genre
    )
    if not response:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return response
