from http import HTTPStatus
from typing import Optional, Type

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import HTTPException
from pydantic import BaseModel

from src.models.film import FilmShort
from src.models.person import Person
from src.services import AsyncSearchEngine


class ElasticSearchEngine(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index_name: str, id_: str):
        """Берем данные по id"""
        return await self.elastic.get(index=index_name, id=id_)

    async def get_all(
            self,
            model: Type[BaseModel],
            index_name: str,
            sort: Optional[str] = None,
            filter_genre: Optional[str] = None,
    ) -> list:
        """получаем все данные из эластика, параметры сортировки и пагинация учтены"""
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

    async def get_sorted_films(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
    ) -> Optional[list[FilmShort]]:
        """достает фильмы из эластика, учитывая сортировку по переданным параметрам"""
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

    async def get_person_films(self, ids: list[str]) -> list[FilmShort]:
        """поиск фильмов по персонам в них"""
        try:
            res = await self.elastic.mget(body={"ids": ids}, index="movies")
        except NotFoundError:
            return []
        return [FilmShort(**doc["_source"]) for doc in res["docs"]]

    async def get_persons(
            self,
            page_number: int,
            page_size: int,
            query: Optional[str] = None,
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
