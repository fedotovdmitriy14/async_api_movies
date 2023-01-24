from http import HTTPStatus
from typing import Optional, Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from pydantic import BaseModel

from src.models.film import FilmShort, FilmDetail
from src.models.genre import Genre
from src.models.person import PersonShort, Person

Models = (FilmShort, FilmDetail, Genre, PersonShort, Person)
ES_models = Union[Models]

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # async def make_redis_key(self, index_name: str, item_id: str):
    #     return f'{index_name}::{item_id}'

    async def _data_from_cache(self, model: ES_models, item_id: str) -> Optional[ES_models]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(f'{model.__class__.__name__}::{item_id}')
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        return model.parse_raw(data)

    async def _put_data_to_cache(self, model: ES_models):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            f'{model.__class__.__name__}::{model.uuid}',
            model.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_all(
            self,
            model: Type[BaseModel],
            index_name: str,
            sort: Optional[str] = None,
            filter_genre: Optional[str] = None,
    ) -> list:
        body = {'query': {'match_all': {}}}
        if filter_genre:
            body = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'nested': {
                                    'path': 'genre',
                                    'query': {
                                        'bool': {
                                            'should': [
                                                {
                                                    'term':
                                                        {
                                                            'genre.id': filter_genre,
                                                        }
                                                }
                                            ]
                                        }
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        if sort:
            order = 'asc'
            if sort[0] == '-':
                order = 'desc'
                sort = sort[1:]
            if sort in model.__annotations__:
                body.update({'sort': [{sort: {'order': order}}]})
        document = await self.elastic.search(index=index_name, body=body)
        result = [model(**hit["_source"]) for hit in document["hits"]["hits"]]
        if not result:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'{index_name} not found')
        return result

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(
            self,
            id_: str,
            model: ES_models,
            index_name: str,
    ):
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        res = self._data_from_cache(model, id_)
        if not res:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            try:
                res = await self.elastic.get(index=index_name, id=id_)
            except NotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'no {index_name} with this id')
            res = res['_source']
            # Сохраняем фильм  в кеш
            await self._put_data_to_cache(rec := model(**res))
            return rec

        return res
