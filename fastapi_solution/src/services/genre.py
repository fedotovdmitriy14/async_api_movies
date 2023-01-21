from functools import lru_cache
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends, HTTPException
from typing import Optional

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(
            self,
            sort: Optional[str] = None
    ) -> Optional[list[Genre]]:
        body = {'query': {'match_all': {}}}
        if sort:
            order = 'asc'
            if sort[0] == '-':
                order = 'desc'
                sort = sort[1:]
            if sort in Genre.__annotations__:
                body.update({'sort': [{sort: {'order': order}}]})
        try:
            document = await self.elastic.search(index='genres', body=body)
            return [Genre(**hit["_source"]) for hit in document["hits"]["hits"]]
        except NotFoundError:
            return None


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)