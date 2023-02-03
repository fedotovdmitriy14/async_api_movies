import json
from typing import Optional, Union

from aioredis import Redis

from src.core.config import settings
from src.models.film import FilmShort, FilmDetail
from src.models.genre import Genre
from src.models.person import PersonShort, Person
from src.services import AbstractStorage


Models = (FilmShort, FilmDetail, Genre, PersonShort, Person)


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
