from functools import lru_cache
from http import HTTPStatus

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from typing import Optional

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import Person, PersonShort


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

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
                        'should': [
                            {'match': {'full_name': query}},
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

    async def get_by_id(self, person_id: str) -> Optional[PersonShort]:
        person = None   # пока нет redis
        if not person:
            try:
                person = await self.elastic.get('persons', person_id)
            except NotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='no person with this id')
            person = person['_source']
            # Сохраняем персону в кеш
            # await self._put_person_to_cache(film)
        return PersonShort(**person)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
