from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from typing import Optional

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.services.base_service import BaseService


class PersonService(BaseService):
    async def get_persons(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
    ):
        return await self.db_engine.get_persons(page_number=page_number, page_size=page_size, query=query)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
