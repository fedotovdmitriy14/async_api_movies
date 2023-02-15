from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.base_service import BaseService


class FilmService(BaseService):
    async def get_sorted_films(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
    ):
        return await self.db_engine.get_sorted_films(page_number=page_number, page_size=page_size, query=query)

    async def get_person_films(self, ids: list[str]):
        return await self.db_engine.get_person_films(ids=ids)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
