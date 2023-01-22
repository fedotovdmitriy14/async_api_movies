from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from typing import Optional

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import Person
from src.services.base import BaseService


class PersonService(BaseService):
    async def get_persons(
            self,
            query: Optional[str] = None,
            page_number: Optional[int] = None,
            page_size: Optional[int] = None,
    ) -> Optional[list[Person]]:
        body = {'query': {'match_all': {}}}
        if query:
            body = {
                'query': {
                    'bool': {
                        'must': [
                            {'match': {'name': query}},
                        ]
                    }
                }
            }
        if page_number and page_size and 10000 > page_size >= 0 and page_number > 0:
            body.update(
                {
                    'size': page_size,
                    'from': (page_number - 1) * page_size,
                }
            )
        try:
            document = await self.elastic.search(index='persons', body=body)
            return [Person(**hit["_source"]) for hit in document["hits"]["hits"]]
        except NotFoundError:
            return None


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
