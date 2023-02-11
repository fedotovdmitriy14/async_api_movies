from typing import Optional, List
from fastapi import APIRouter, Depends, Query

from src.models.film import FilmShort
from src.models.person import Person
from src.services.film import FilmService, get_film_service
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/",
    response_model=List[Person],
    summary="Get all persons",
    description="Persons main"
)
async def get_all_persons(
        page_number: Optional[int] = Query(alias='page[number]', default=1, gt=0),
        page_size: Optional[int] = Query(alias='page[size]', default=10, gt=0, lt=10000),
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    return await person_service.get_persons(page_number=page_number, page_size=page_size)


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Get detailed person by id",
    description="Person detailed info"
)
async def person_details(
        person_id: str,
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    return await person_service.get_by_id(
        id_=person_id,
        model=Person,
        index_name='persons')


@router.get(
    "/{person_id}/film",
    response_model=list[FilmShort],
    summary="Get all films by person id",
    description="All films by person id",
)
async def person_films(
    person_id: str,
    person_service: PersonService = Depends(get_person_service),
    film_service: FilmService = Depends(get_film_service),
) -> list[FilmShort]:
    es_person = await person_service.get_by_id(
        id_=person_id,
        model=Person,
        index_name='persons')
    return await film_service.get_person_films(es_person.film_ids)


@router.get(
    "/search/",
    response_model=list[Person],
    description="Search persons",
    summary="Search persons",
)
async def search_person(
    query: Optional[str] = Query(default=None),
    page_number: Optional[int] = Query(alias='page[number]', default=1, gt=0),
    page_size: Optional[int] = Query(alias='page[size]', default=10, gt=0, lt=10000),
    person_service: PersonService = Depends(get_person_service),
) -> Optional[list[Person]]:
    return await person_service.get_persons(query=query, page_number=page_number, page_size=page_size)
