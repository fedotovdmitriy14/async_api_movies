from models.base import AbstractModel
from typing import Optional, List


class PersonShort(AbstractModel):
    full_name: str


class Person(PersonShort):
    roles: Optional[List[str]]
    film_ids: Optional[List[str]]
