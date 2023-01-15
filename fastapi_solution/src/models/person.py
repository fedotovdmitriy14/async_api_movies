from models.base import AbstractModel
from pydantic.schema import Dict


class Person(AbstractModel):
    full_name: str
    roles: Dict
