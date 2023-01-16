from pydantic import Field

from models.base import AbstractModel
from typing import Optional, List


class PersonShort(AbstractModel):
    full_name: str = Field(alias="name")


class Person(PersonShort):
    roles: Optional[List[str]] = None
    film_ids: Optional[List[str]] = None
