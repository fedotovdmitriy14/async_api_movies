from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Объект router, в котором регистрируем обработчики
from src.db.elastic import get_elastic
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


@router.get('/')
async def get_all_films(db: AsyncElasticsearch = Depends(get_elastic)):
    films = FilmService(redis=None, elastic=db)
    return {'response': f'{films.get_all_films()}'}


@router.get('test')
async def get_test(db = Depends(get_elastic)):
    print(f'{await db.ping()=}')

    return {'response': 1}
