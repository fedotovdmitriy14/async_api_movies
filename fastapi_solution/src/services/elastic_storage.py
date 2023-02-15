from elasticsearch import AsyncElasticsearch

from src.services import AsyncSearchEngine


class ElasticStorage(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index_name: str, id_: str):
        """Берем данные по """
        return await self.elastic.get(index=index_name, id=id_)

    async def get_all(self, index_name: str, body: dict):
        """кладем запись в кеш"""
        return await self.elastic.search(index=index_name, body=body)
