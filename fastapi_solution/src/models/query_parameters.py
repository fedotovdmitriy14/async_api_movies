from typing import Optional

from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    sort: Optional[str]
    page_number: Optional[int] = Field(alias="page[number]")
    # page_size: Optional[int] = Field(alias="page[size]")
    # filter_genre: Optional[str] = Field(alias="filter[genre]")


# print(QueryParams.__annotations__)
