import json
from http import HTTPStatus
from typing import Optional, Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from pydantic import BaseModel

from src.core.config import settings
from src.models.film import FilmShort, FilmDetail
from src.models.genre import Genre
from src.models.person import PersonShort, Person
from src.services import AbstractStorage

Models = (FilmShort, FilmDetail, Genre, PersonShort, Person)


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.redis_storage = RedisStorage(redis=self.redis)

    async def get_all(
            self,
            model: Type[BaseModel],
            index_name: str,
            sort: Optional[str] = None,
            filter_genre: Optional[str] = None,
    ) -> list:
        """получаем все данные из эластика, параметры сортировки и пагинация учтены"""
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

    async def get_by_id(
            self,
            id_: str,
            model: Union[Models],
            index_name: str,
    ):
        """проверяется, есть ли запись в кеше; если нет - достается из эластика"""
        res = await self.redis_storage.data_from_cache(index_name, model, id_)
        if not res:
            try:
                res = await self.elastic.get(index=index_name, id=id_)
            except NotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'no {index_name} with this id')
            res = res['_source']

            await self.redis_storage.put_data_to_cache(index_name, res)
            return model(**res)

        return res


class RedisStorage(AbstractStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def data_from_cache(self, index_name: str, model: Union[Models], item_id: str) -> Optional[Union[Models]]:
        """пробуем получить запись по id из кеша"""
        data = await self.redis.get(f'{index_name}::{item_id}')
        if not data:
            return None

        return model.parse_raw(data)

    async def put_data_to_cache(self, index_name: str, model: dict) -> None:
        """кладем запись в кеш"""
        await self.redis.set(
            f'{index_name}::{model["id"]}',
            json.dumps(model),
            expire=settings.redis_cache_time
        )
