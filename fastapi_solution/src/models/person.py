from pydantic import Field
from typing import Optional, List

from src.models.base import AbstractModel


class PersonShort(AbstractModel):
    full_name: str = Field(alias="name")


class Person(PersonShort):
    roles: Optional[List[str]] = None
    film_ids: Optional[List[str]] = None
