from functools import lru_cache
from http import HTTPStatus
from typing import Optional, Type, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException, Depends
from pydantic import BaseModel

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.elastic_engine import ElasticSearchEngine
from src.services.redis_storage import RedisStorage, Models


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.redis_storage = RedisStorage(redis=self.redis)
        self.db_engine = ElasticSearchEngine(elastic=self.elastic)

    async def get_all(
            self,
            model: Type[BaseModel],
            index_name: str,
            sort: Optional[str] = None,
            filter_genre: Optional[str] = None,
    ):
        return await self.db_engine.get_all(index_name=index_name, model=model, sort=sort, filter_genre=filter_genre)

    async def get_by_id(self, index_name: str, id_: str, model: Union[Models]):
        res = await self.redis_storage.data_from_cache(index_name, model, id_)
        print(f'{res=}')
        if not res:
            try:
                res = await self.db_engine.get_by_id(index_name=index_name, id_=id_)
            except NotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'no {index_name} with this id')
            res = res['_source']

            await self.redis_storage.put_data_to_cache(index_name, res)
            return model(**res)

        return res

    async def get_sorted_films(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
    ):
        return await self.db_engine.get_sorted_films(page_number=page_number, page_size=page_size, query=query)

    async def get_person_films(self, ids: list[str]):
        return await self.db_engine.get_person_films(ids=ids)

    async def get_persons(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
    ):
        return await self.db_engine.get_persons(page_number=page_number, page_size=page_size, query=query)


@lru_cache()
def get_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseService:
    return BaseService(redis, elastic)
