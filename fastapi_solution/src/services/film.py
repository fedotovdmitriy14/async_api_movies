from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import FilmShort
from src.services.base import BaseService


# FilmService содержит бизнес-логику по работе с фильмами.
# Никакой магии тут нет. Обычный класс с обычными методами.
# Этот класс ничего не знает про DI — максимально сильный и независимый.
class FilmService(BaseService):
    async def get_sorted_films(
            self,
            query: Optional[str] = None,
            page_number: Optional[int] = None,
            page_size: Optional[int] = None,
    ) -> Optional[list[FilmShort]]:
        body = {'query': {'match_all': {}}}
        if query:
            body = {
                'query': {
                    'bool': {
                        'should': [
                            {'match': {'title': query}},
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
        document = await self.elastic.search(index='movies', body=body)
        result = [FilmShort(**hit["_source"]) for hit in document["hits"]["hits"]]
        if not result:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
        return result

    async def get_person_films(self, ids: list[str]):
        try:
            res = await self.elastic.mget(body={"ids": ids}, index="movies")
        except NotFoundError:
            return []
        return [FilmShort(**doc["_source"]) for doc in res["docs"]]


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
