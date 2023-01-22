from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.film import FilmShort
from src.models.person import Person, PersonShort
from src.services.film import FilmService, get_film_service
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Get detailed person by id",
    description="Person detailed info"
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Person:
    person = await person_service.get_by_id(
        id_=person_id,
        model=Person,
        index_name='persons')
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Person with uuid {0} not found".format(person_id)
        )
    return person


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
    person_films = await film_service.get_person_films(es_person.film_ids)
    return person_films


@router.get(
    "/search/",
    response_model=list[Person],
    description="Search persons",
    summary="Search persons",
)
async def search_person(
    query: Optional[str] = Query(default=None),
    page_number: Optional[int] = Query(None, alias='page[number]'),
    page_size: Optional[int] = Query(None, alias='page[size]'),
    person_service: PersonService = Depends(get_person_service),
) -> Optional[list[Person]]:
    es_persons = await person_service.get_persons(query=query, page_number=page_number, page_size=page_size)
    if not es_persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return es_persons
