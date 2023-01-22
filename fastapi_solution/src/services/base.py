from http import HTTPStatus
from typing import Optional, Type

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import HTTPException
from pydantic import BaseModel


class BaseService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_all(
            self,
            model: Type[BaseModel],
            index_name: str,
            sort: Optional[str] = None,
            filter_genre: Optional[str] = None,
    ) -> list:
        body = {'query': {'match_all': {}}}
        if filter_genre:
            body = {
                'query': {
                    'bool': {
                        'must': [
                            {
                                'nested': {
                                    'path': 'genre',
                                    'query': {
                                        'bool': {
                                            'should': [
                                                {
                                                    'term':
                                                        {
                                                            'genre.id': filter_genre,
                                                        }
                                                }
                                            ]
                                        }
                                    },
                                }
                            }
                        ]
                    }
                }
            }
        if sort:
            order = 'asc'
            if sort[0] == '-':
                order = 'desc'
                sort = sort[1:]
            if sort in model.__annotations__:
                body.update({'sort': [{sort: {'order': order}}]})
        document = await self.elastic.search(index=index_name, body=body)
        result = [model(**hit["_source"]) for hit in document["hits"]["hits"]]
        if not result:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'{index_name} not found')
        return result
