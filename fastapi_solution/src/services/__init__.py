from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel


class AbstractStorage(ABC):
    @abstractmethod
    async def data_from_cache(self, index_name: str, model: [Type[BaseModel]], item_id: str) -> None:
        pass

    @abstractmethod
    async def put_data_to_cache(self, index_name: str, model: dict) -> None:
        pass


class AsyncSearchEngine(ABC):

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_by_id(self, *args, **kwargs):
        pass

