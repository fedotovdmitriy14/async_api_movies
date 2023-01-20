from typing import Optional, Union
from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from core.config import *
from models.genre import Genre
from models.person import Person

ESIndex = (Genre, Person)


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.redis = redis
        self.elastic = elastic
        self.index = index

    async def _data_from_cache(self, data_id: str, index: ESIndex) -> Optional[Union[ESIndex]]:
        data = await self.redis.get(data_id)
        if not data:
            return None

        film = index.parse_raw(data)
        return film

    async def _put_data_to_cache(self, key, value):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(key, value, expire=CACHE_EXPIRE_IN_SECONDS)

    async def search_in_elastic(self, body: dict, schema: ESIndex) -> Optional[Union[ESIndex]]:
        try:
            docs = await self.elastic.search(index=self.index, body=body)
            return [schema(**row["_source"]) for row in docs["hits"]["hits"]]
        except NotFoundError:
            return None