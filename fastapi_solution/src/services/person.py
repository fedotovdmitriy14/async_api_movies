from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from typing import Optional
from http import HTTPStatus

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
        document = await self.elastic.search(index='persons', body=body)
        result = [Person(**hit["_source"]) for hit in document["hits"]["hits"]]
        if not result:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
        return result


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
